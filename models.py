from django.db import models

# Create your models here.
class Approbateur(models.Model):
    approbateur = models.CharField(db_column='approbateur',  max_length=50)  
    approb_id = models.AutoField(primary_key=True)

    def LoadFromCSVLine(self, csvline):
        self.approbateur = csvline["APPROBATEUR"]


#Create your models here.
class Contrat(models.Model):
    contrat_id = models.AutoField(primary_key=True)
    numero = models.CharField(db_column='numero', max_length=50)  
    fournisseur = models.CharField(db_column='fournisseur', max_length=50)  # Field name made lowercase.
    date = models.DateField(db_column='date')  
    approbateur = models.CharField(db_column='approbateur',  max_length=50)  
    description = models.TextField(db_column='description', blank=True, null=True) 
    service = models.CharField(db_column='service',  max_length=50)  
    activite = models.CharField(db_column='activite',  max_length=50) 
    montant = models.FloatField(db_column='montant') 


    def LoadFromCSVLine(self, csvline):
        #type, md5, contrat, path, sha1, arguments
        self.numero = csvline["NUMÉRO"]
        self.fournisseur = csvline["NOM DU FOURNISSEUR"]
        self.date = csvline["DATE D'APPROBATION"]
        self.approbateur = csvline["APPROBATEUR"]
        self.description = csvline["DESCRIPTION"]
        self.service = csvline["SERVICE"]
        self.activite = csvline["ACTIVITÉ"]
        self.montant = float(csvline["MONTANT"].replace(",","."))