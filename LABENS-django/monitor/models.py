from django.db import models

# Create your models here.

class Campus(models.Model):
    cod = models.CharField(max_length=2,primary_key=True)
    nome = models.CharField(max_length=20)
    id = models.IntegerField()
    estTipo = models.IntegerField()

    def __str__(self):
        return(self.nome)

class FaixasIP(models.Model):
    pref= models.CharField(max_length=15,primary_key=True)
    descri = models.CharField(max_length=15)

    def __str__(self):
        return(self.descri)

class InvConfig(models.Model):
    fpTipoOpts = (('D','Delay'),('A','Advance'))
    StatusOpts = (('A','Applied'),('U','Updated'))
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE)
    nome = models.CharField(max_length=4)
    descri = models.TextField()
    fp = models.DecimalField(max_digits=3,decimal_places=2)
    fpTipo = models.CharField(max_length=1,choices=fpTipoOpts)
    fpMin = models.DecimalField(max_digits=3,decimal_places=2)
    fpMax = models.DecimalField(max_digits=3,decimal_places=2)
    limPot = models.IntegerField()
    UpdateStatus = models.CharField(max_length=1,choices=StatusOpts)
    UpdateTime = models.DateTimeField()

    def __str__(self):
        return (self.campus.nome+" "+self.nome)

    class Meta:
        unique_together = (("campus","nome"),)

class InvConfigTokens(models.Model):
    token = models.CharField(max_length=255,primary_key=True)
    inverters = models.ManyToManyField(InvConfig)
