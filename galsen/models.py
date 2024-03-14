from django.db import models

from django.contrib.auth.models import AbstractUser as BaseAbstractUser, BaseUserManager, Permission, Group
from django.conf import settings
from django.urls import reverse


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        # Votre implémentation pour créer un utilisateur
        pass

    def create_superuser(self, email, username, password=None, **extra_fields):
        # Votre implémentation pour créer un superutilisateur
        pass

class AbstractUser(BaseAbstractUser):
    # Ajoutez ces deux lignes avec related_name
    groups = models.ManyToManyField(Group, related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set', blank=True)


# Create your models here.
class CustomUser(AbstractUser):
    ROLES = [
        ('admin', 'Admin'),
        ('personnel', 'Personnel(le)'),
        ('ecole', 'Ecole'),
        ('entreprise', 'Entreprise'),
    ]
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    banner_image = models.ImageField(upload_to='banner_images/', null=True, blank=True)
    GENRE = [
        ('homme', 'Homme'),
        ('femme', 'Femme'),
    ]
    SITUATION_MATRIMONIALE = [
        ('celibataire', 'Célibataire'),
        ('marie', 'Marié(e)'),
        ('fiance', 'Fiancé(e)'),
        ('divorce', 'Divorcé(e)'),
    ]
    marque_dispositif = models.CharField(max_length=255, null=True, blank=True)
    metier = models.CharField(max_length=150, null=True, blank=True)
    pays = models.CharField(max_length=50, null=True, blank=True)
    ville = models.CharField(max_length=50, null=True, blank=True)
    quartier = models.CharField(max_length=50, null=True, blank=True)
    langue = models.CharField(max_length=255, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    indicatif_pays = models.CharField(max_length=15, null=True, blank=True)
    number_phone = models.CharField(max_length=15, null=True, blank=True)
    number_whatsapp = models.CharField(max_length=15, null=True, blank=True)
    number_telegram = models.CharField(max_length=15, null=True, blank=True)
    instagram_link = models.URLField(null=True, blank=True)
    twitter_link = models.URLField(null=True, blank=True)
    youtube_link = models.URLField(null=True, blank=True)
    website_link = models.URLField(null=True, blank=True)
    rôle = models.CharField(max_length=255, choices=ROLES, default='personnel')
    genre = models.CharField(max_length=255, choices=GENRE, default='homme')
    situation_matrimoniale = models.CharField(max_length=20, choices=SITUATION_MATRIMONIALE, default='celibataire')
    
    def get_absolute_url(self):
        return reverse('a_propos_current_user')
  
class Profil(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    description = models.TextField()
    
class Experience(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    
class Formation(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    
class Abonnement(models.Model):
    user_a = models.ForeignKey(CustomUser, related_name='user_a_subscriptions', on_delete= models.CASCADE)
    user_b = user_b = models.ForeignKey(CustomUser, related_name='user_b_subscriptions', on_delete= models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    
class Post(models.Model):
    CATEGORIES = [
        ('poste', 'Poste'),
        ('even', 'Even'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    video = models.FileField(upload_to='post_videos/')
    contenu_post = models.TextField()
    tag_post = models.CharField(max_length=255)
    categories = models.CharField(max_length=255, choices=CATEGORIES, default='poste')
    session_info = models.CharField(max_length=255, null=True, blank=True)
    date_creation_post = models.DateTimeField(auto_now_add=True)
    like_post = models.ManyToManyField(CustomUser, blank=True, related_name="likes")
    dislike = models.ManyToManyField(CustomUser, blank=True, related_name='dislikes')
    shared_boby = models.TextField(blank=True, null=True)
    share_on = models.DateTimeField(blank=True, null=True)
    shared_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='+')
    
    class Meta:
        ordering = ['-date_creation_post', '-share_on']

    @property
    def nombre_commentaire(self):
        return Commentaire.objects.filter(post=self).count()
    
class MediasPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post_images/')
    
class Commentaire(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    contenu_commentaire = models.TextField()
    image = models.ImageField(upload_to='comment_images/')
    date_creation = models.DateTimeField(auto_now_add=True)
    
    @property
    def nombre_response(self):
        return Reponse.objects.filter(comment=self).count()
    
class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    
class Share(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    
class Reponse(models.Model):
    commentaire = models.ForeignKey(Commentaire, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    contenu_text = models.TextField()
    image = models.ImageField(upload_to='response_images/')
    date_creation = models.DateTimeField(auto_now_add=True)
    
class Job(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True, blank=True)
    contenu_job = models.TextField()
    date_creation_post = models.DateTimeField(auto_now_add=True)
    
class Postule(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    
class ShareJob(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    
class Boutique(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    nom_boutique = models.CharField(max_length=255)
    devise_boutique = models.CharField(max_length=255)
    description = models.TextField()
    photo_profil = models.ImageField(upload_to='boutique_profil/')
    banner_image = models.ImageField(upload_to='boutique_banner/')
    date_creation = models.DateField(auto_now_add=True)
    
class Client(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    boutique = models.ForeignKey(Boutique, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    
class Product(models.Model):
    boutique = models.ForeignKey(Boutique, on_delete=models.CASCADE)
    video = models.FileField(upload_to='product_videos/')
    nom_produit = models.CharField(max_length=255)
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    quantite_stock = models.IntegerField(null=True, blank=True)
    fournisseur = models.CharField(max_length=255)
    date_creation = models.DateTimeField(auto_now_add=True)
    
class MediasProduct(models.Model):
    produit = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')