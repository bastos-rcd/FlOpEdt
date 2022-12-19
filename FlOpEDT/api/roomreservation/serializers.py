from django.db.models import Max
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from api.people.serializers import ShortUsersSerializer
from api.fetch.serializers import IDRoomSerializer

import roomreservation.models as rm
from roomreservation.check_periodicity import check_periodicity, check_reservation

from django.core.mail import EmailMessage

class PeriodicityField(serializers.Field):
    def to_representation(self, value):
        return ReservationPeriodicitySerializer.get_data(value)

    def to_internal_value(self, data):
        periodicity = data['periodicity']
        serialized = ReservationPeriodicitySerializer.get_serializer(periodicity)(data=periodicity)
        if serialized.is_valid():
            return serialized.validated_data
        raise ValidationError(serialized.errors)

    def get_attribute(self, instance):
        return instance

    def get_value(self, instance):
        return instance


class ReservationPeriodicitySerializer(serializers.Serializer):
    periodicity = PeriodicityField()

    class Meta:
        model = rm.ReservationPeriodicity
        fields = ['periodicity']

    @staticmethod
    def get_model(arg):
        if isinstance(arg, rm.ReservationPeriodicity):
            periodicity_type = arg.periodicity_type
            if periodicity_type == 'BW':
                return rm.ReservationPeriodicityByWeek
            if periodicity_type == 'BM':
                return rm.ReservationPeriodicityByMonth
            if periodicity_type == 'EM':
                return rm.ReservationPeriodicityEachMonthSameDate
        if isinstance(arg, dict):
            periodicity_type = arg['periodicity_type']
            if periodicity_type == 'BW':
                return rm.ReservationPeriodicityByWeek
            if periodicity_type == 'BM':
                return rm.ReservationPeriodicityByMonth
            if periodicity_type == 'EM':
                return rm.ReservationPeriodicityEachMonthSameDate

    @staticmethod
    def get_serializer(arg):
        if isinstance(arg, rm.ReservationPeriodicity):
            periodicity_type = arg.periodicity_type
            if periodicity_type == 'BW':
                return ReservationPeriodicityByWeekSerializer
            if periodicity_type == 'BM':
                return ReservationPeriodicityByMonthSerializer
            if periodicity_type == 'EM':
                return ReservationPeriodicityEachMonthSameDateSerializer
        if isinstance(arg, dict):
            periodicity_type = arg['periodicity_type']
            if periodicity_type == 'BW':
                return ReservationPeriodicityByWeekSerializer
            if periodicity_type == 'BM':
                return ReservationPeriodicityByMonthSerializer
            if periodicity_type == 'EM':
                return ReservationPeriodicityEachMonthSameDateSerializer

    @staticmethod
    def get_data(obj):
        values = ReservationPeriodicitySerializer.get_model(obj).objects.filter(id=obj.id)
        if len(values) == 0:
            return {}
        return ReservationPeriodicitySerializer.get_serializer(obj)(values[0]).data


class ConflictError(ValidationError):
    status_code = status.HTTP_409_CONFLICT


def create_reservations_if_possible(periodicity, original_reservation, create_repetitions: bool = False):
    # Run the verification
    check = check_periodicity(periodicity, original_reservation)
    # Get the reservations which do not conflict
    ok_reservations = check['ok_reservations']
    # Get the reservations which conflict
    nok_reservations = check['nok_reservations']
    # Get the verification status
    are_reservations_all_possible = check['status'] == 'OK'
    if not are_reservations_all_possible:
        # There are conflicts
        if not create_repetitions:
            # Do not create possible reservations, inform the client instead
            raise ConflictError(
                {
                    "periodicity": {
                        "ok_reservations": ok_reservations,
                        "nok_reservations": nok_reservations,
                    }
                }
            )
    # No conflict or must create the possible reservations, proceed to the registration
    # Get the corresponding periodicity model
    model = ReservationPeriodicitySerializer.get_model(periodicity)
    # Create a new periodicity instance
    
    
    if periodicity['id'] < 0:
        # Generate a new ID if negative
        periodicity.pop('id')
        periodicity_instance = model.objects.create(**periodicity)
    else:
        periodicity_instance = model.objects.get(id=periodicity['id'])

    # Create the future reservations
    for reservation in ok_reservations:
        # Ignore the current reservation in the list
        if reservation['date'] != original_reservation['date'].isoformat():
            reservation['periodicity'] = periodicity_instance
            rm.RoomReservation.objects.create(**reservation)
    return periodicity_instance


def check_reservation_possible(reservation):
    check = check_reservation(reservation)
    if check['status'] == 'NOK':
        # There are conflicts
        raise ConflictError({
            "periodicity": {
                "nok_reservations": check['more'],
            }
        })


class RoomReservationSerializer(serializers.ModelSerializer):
    periodicity = ReservationPeriodicitySerializer(allow_null=True)
    create_repetitions = serializers.BooleanField(write_only=True, default=False)

    def create(self, validated_data):
        check_reservation_possible(validated_data)
        periodicity = validated_data.pop('periodicity')
        # Check if we should create repeated reservations
        create_repetitions = False
        if 'create_repetitions' in validated_data:
            create_repetitions = validated_data.pop('create_repetitions')

        if periodicity:
            # Multiple reservations, try to create them
            # Get the internal periodicity data
            periodicity = periodicity['periodicity']

            # Create the reservations or inform the client
            periodicity_instance = create_reservations_if_possible(periodicity, validated_data, create_repetitions)
            # Store the instance to the reservation
            validated_data['periodicity'] = periodicity_instance
        room = validated_data['room']
        reservation = rm.RoomReservation.objects.create(**validated_data)
        if rm.RoomReservationValidationEmail.objects.filter(room=room).exists():
            validators = rm.RoomReservationValidationEmail.objects.get(room=room).validators.all()
            responsible = validated_data['responsible']
            date = validated_data['date']
            title = validated_data['title']
            url = ""
            subject = f"{room.name} : nouvelle réservation le {date}"
            message = f"{responsible.first_name} {responsible.last_name} a réservé la {room.name}"
            message += f" le {date} de {validated_data['start_time']} à {validated_data['end_time']} "
            if periodicity:
                message += f"(et plusieurs autres jours aux mêmes horaires) "
            message += f"avec le titre {title}.\n\n"
            # TODO : tester le lien de suppression!
            if url:
                message += "Vous pouvez la supprimer :\n"\
                           "- via l'interface de réservation : "\
                           f"{url}/fr/roomreservation/{responsible.departments.first().abbrev}/\n"\
                           "ou en cliquant ici: " \
                           f"{url}/fr/api/roomreservations/reservation/{reservation.id}/\n\n"
            message += "Message envoyé automatiquement par flop!EDT."
            for validator in validators:
                email = EmailMessage(
                    subject=subject,
                    body=f"Bonjour {validator.first_name}\n \n" + message,
                    to=[validator.email],
                    bcc=[]
                )
                email.send()
        return reservation

    def update(self, instance, validated_data):
        """
        Updates the values of given RoomReservation.
        Cannot alter an existing periodicity, only add a new one or unlink it.
        """
        instance.responsible = validated_data.get('responsible', instance.responsible)
        instance.room = validated_data.get('room', instance.room)
        instance.reservation_type = validated_data.get('reservation_type', instance.reservation_type)
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.email = validated_data.get('email', instance.email)
        instance.date = validated_data.get('date', instance.date)
        instance.start_time = validated_data.get('start_time', instance.start_time)
        instance.end_time = validated_data.get('end_time', instance.end_time)

        # Periodicity process
        # Add the reservation id to ignore conflicts with its previous date
        reservation_data = validated_data
        reservation_data['id'] = instance.id

        # Check if we should create repeated reservations
        create_repetitions = False
        if 'create_repetitions' in validated_data:
            create_repetitions = validated_data.pop('create_repetitions')

        # Get the periodicity
        periodicity = validated_data.pop('periodicity', instance.periodicity)
        if periodicity:
            # Has a periodicity
            # Get its data
            periodicity = periodicity['periodicity']
            if 'id' in periodicity and periodicity['id'] > 0:
                # The changes do not concern the periodicity, check if they can be applied
                check_reservation_possible(reservation_data)
            else:
                # If 'id' is not in the periodicity or the id is present and negative that means a new periodicity
                # for the reservation
                periodicity_instance = create_reservations_if_possible(periodicity, reservation_data, create_repetitions)
                instance.periodicity = periodicity_instance
        else:
            # Does not have a periodicity, check if the reservation is possible
            check_reservation_possible(reservation_data)
            instance.periodicity = None
        instance.save()
        return instance

    class Meta:
        model = rm.RoomReservation
        fields = '__all__'


class ShortRoomReservationSerializer(serializers.ModelSerializer):
    responsible = ShortUsersSerializer()
    room = IDRoomSerializer()

    class Meta:
        model = rm.RoomReservation
        fields = ('date', 'start_time', 'end_time', 'title', 'room', 'responsible')


class RoomReservationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = rm.RoomReservationType
        fields = '__all__'


class ReservationPeriodicityByWeekSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = rm.ReservationPeriodicityByWeek
        fields = '__all__'


class ReservationPeriodicityEachMonthSameDateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = rm.ReservationPeriodicityEachMonthSameDate
        fields = '__all__'


class ReservationPeriodicityByMonthSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = rm.ReservationPeriodicityByMonth
        fields = '__all__'
