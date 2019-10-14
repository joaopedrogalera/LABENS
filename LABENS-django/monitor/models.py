from django.db import models

# Create your models here.

class Campus(models.Model):
    cod = models.CharField(max_length=2,primary_key=True)
    nome = models.CharField(max_length=20)
    id = models.IntegerField()
    estTipo = models.IntegerField()

    def __str__(self):
        return(self.nome)
