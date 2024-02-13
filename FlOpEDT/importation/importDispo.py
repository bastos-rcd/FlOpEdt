from django.conf import settings
from base.models import UserAvailability, Time, Day, Slot
from people.models import User
import os
import csv

import xlrd

def handle_uploaded_file_xlsx(file):
    with open('{}/dispo.xlsx'.format(settings.MEDIA_ROOT), 'wb+') as dest:
        for chunk in file.chunks():
            dest.write(chunk)
    #csv_from_excel('FlOpEDT/importation/test2.xlsx')
    return "FlOpEDT/importation/dispo.xlsx"

def handle_uploaded_file_csv(file):
    with open('{}/your_csv_file.csv'.format(settings.MEDIA_ROOT), 'wb+') as dest:
        for chunk in file.chunks():
            dest.write(chunk)
    #csv_from_excel('FlOpEDT/importation/test2.xlsx')
    return "FlOpEDT/importation/your_csv_file.xlsx"

def verif_file(file):
    if file.name.endswith(('.csv')):
        csv_file = handle_uploaded_file_csv(file)
        #csvreader(csv_file)
        #os.remove(file) #Ligne à enlever si on souhaite garder le fichier

    elif file.name.endswith(('.xlsx')):
        xlsx_file = handle_uploaded_file_xlsx(file) # récupération
        csv_file = csv_from_excel(xlsx_file) # transformation
        #csvreader(csv_file)
        os.remove(csv_file) #Ligne à enlever si on souhaite garder le fichier csv
        os.remove(xlsx_file) #Ligne à enlever si on souhaite garder le fichier xlsx

    else:
        ... #Si le fichier n'est pas un csv ou xlsx alors sa ne fait rien

#transforme un fichier excel en fichier csv
def csv_from_excel(file):
    wb = xlrd.open_workbook(file)
    sh = wb.sheet_by_name('Feuille 1')
    your_csv_file = open('{}/your_csv_file.csv'.format(settings.MEDIA_ROOT), 'w')
    wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)

    for rownum in range(sh.nrows):
        wr.writerow(sh.row_values(rownum))

    your_csv_file.close()
    return your_csv_file.name

#preconditions :
#tous les users sont deja present dans la base de donnee

#0 Annee [year,n°anne,nb sem,n°anne,nb sem...]
#1 Semaine[week,n°sem,n°sem,n°sem...]
#2 Creneau [
#3

def csvreader(test):
    with open(test, newline='') as csvfile:
       spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
       i = 1
       j=0
       stockage={}
       l = []
       print(spamreader)
       for row in spamreader:
            print(row)
            a=', '.join(row)
            l=a.split(",")
            stockage[i]=l
            print(l)
            for elem in l:
                 if elem != "" :
                    print(elem)
            print(i)
            i+=1
       print(stockage)
       indiceannee = 2
       indicecreneau = 3
       nbsem=0

       time1 = Time.objects.create(hours=8, minutes=30)
       time2 = Time.objects.create(hours=10, minutes=0)
       time3 = Time.objects.create(hours=14, minutes=00)
       time4 = Time.objects.create(hours=16, minutes=00)
       listecreneau = [time1, time2, time3, time4]
       slot=[]
       Day.objects.create()
       for sem in range(int(stockage[1][2].replace('\"', ''))):
           for day1 in Day.objects.all():
               for slot in listecreneau:
                    slot1 = Slot.objects.create(day=day1, hour=slot, duration="120")
                    print(slot1)
                    slot.append(slot1)
        print(slot)

        for prof in stockage:
            if User.objects:
                day = Day.objects.filter(day="Monday")

                indicevalue = 0
                for value in prof:
                    indicevalue += 1
                    if indicevalue > 2:
                        nouvelledispo = UserAvailability.objects.create(
                            user=User.objects.filter(
                                first_name=prof[0], last_name=prof[1]
                            ),
                            week=stockage[1][j],
                            year=stockage[0][indiceannee],
                            slot=slot1,
                            value=value,
                        )
                        nouvelledispo.save()
                    indicecreneau += 2
        print(stockage[3])
