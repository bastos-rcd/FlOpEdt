import { ComputedRef, Ref } from "vue"
import { BooleanRoomAttributeValue, CourseType, DynamicSelectElementValue, NumericRoomAttributeValue, ReservationPeriodicity, Room, RoomAttribute, RoomReservation, RoomReservationType, User } from "@/type"

export interface RoomAttributeEntry {
    component: any
    value: DynamicSelectElementValue
}

export interface Rooms {
    perDepartmentFilterBySelectedDepartments: ComputedRef<{ [departmentId: string]: Array<Room> }>
    listFilterBySelectedDepartments: ComputedRef<Array<Room>>
    perIdFilterBySelectedDepartments: ComputedRef<{ [roomId: string]: Room }>
    listFilterBySelectedDepartmentsAndFilters: ComputedRef<Array<Room>>
}

export interface CourseTypes {
    perDepartment: Ref<{ [departmentId: string]: Array<CourseType> }>
    listFilterBySelectedDepartments: ComputedRef<Array<CourseType>>
}

export interface RoomReservations {
    list: Ref<Array<RoomReservation>>
    perDay: ComputedRef<{ [day: string]: Array<RoomReservation> }>
}

export interface RoomReservationTypes {
    list: Ref<Array<RoomReservationType>>
    perId: ComputedRef<{ [typeId: string]: RoomReservationType }>
}

export interface ReservationPeriodicities {
    list: Ref<Array<ReservationPeriodicity>>
    perId: ComputedRef<{ [periodicityId: string]: ReservationPeriodicity }>
}

export interface Users {
    list: Ref<Array<User>>
    perId: ComputedRef<{ [userId: string]: User }>
}

export interface RoomAttributes {
    booleanList: Ref<Array<RoomAttribute>>
    numericList: Ref<Array<RoomAttribute>>
}

export interface RoomAttributeValues {
    booleanList: Ref<Array<BooleanRoomAttributeValue>>
    numericList: Ref<Array<NumericRoomAttributeValue>>
}