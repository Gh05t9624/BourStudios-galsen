from django.http import HttpResponse
from django.conf import settings
import os
import time
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm
from django.core.exceptions import ValidationError
from django.contrib import messages
from .decorators import role_required

from .models import CustomUser, Post, MediasPost, Job, Boutique, Commentaire
from django.views.generic import DetailView
from galsen.utils import obtenir_marque_dispositif
from django.http import JsonResponse  


# ========== Details: personnels ===================
class PersonnelDetails(DetailView):
    model = CustomUser
    template_name = 'Personnel/profiles/public_profile/profile_id_personnel.html'
    context_object_name = 'personnel'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print("Contexte de la vue détaillée :", context)
        return context

# ========== Details: Ecole ===================
class EcoleDetails(DetailView):
    model = CustomUser
    template_name = 'Ecole/profiles/public_profile/profile_id_ecole.html'
    context_object_name = 'ecole'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print("Contexte de la vue détaillée :", context)
        return context  
    
# ========== Details: Entreprise ===================
class EntrepriseDetails(DetailView):
    model = CustomUser
    template_name = 'Entreprise/profiles/public_profile/profile_id_entreprise.html'
    context_object_name = 'entreprise'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print("Contexte de la vue détaillée :", context)
        return context 

# ========== Modifier: Post ===================
def update_post(request, id):
    post = get_object_or_404(Post, id=id)
    medias_post = MediasPost.objects.filter(post=post).first()

    if request.method == 'POST':
        # Traitez les données du formulaire et mettez à jour le post
        post.contenu_post = request.POST['contenu_post']
        post.tag_post = request.POST['tag_post']
        post.save()

        # Traitez les médias
        new_image_file = request.FILES.get('image')
        new_video_file = request.FILES.get('video')

        # Supprimez l'ancienne image si elle existe
        if medias_post and medias_post.image and os.path.exists(medias_post.image.path):
            medias_post.image.delete(save=False)

        # Supprimez l'ancienne vidéo si elle existe
        if post.video and os.path.exists(post.video.path):
            post.video.delete(save=False)

        # Mettez à jour la vidéo dans le modèle Post
        if new_video_file:
            post.video = new_video_file
        post.save()

        # Créez ou mettez à jour l'image dans le modèle MediasPost
        if medias_post:
            if new_image_file:
                medias_post.image = new_image_file
            medias_post.save()
        else:
            if new_image_file:
                MediasPost.objects.create(post=post, image=new_image_file)

        user_role = request.user.rôle  # Utilisez 'rôle' selon votre modèle CustomUser
        if user_role == 'admin':
            return redirect('Ad_profile')
        elif user_role == 'personnel':
            return redirect('Per_profile')
        elif user_role == 'ecole':
            return redirect('Ec_profile')
        elif user_role == 'entreprise':
            return redirect('En_profile')

    return render(request, 'formulaires/update/update_post.html', {'post': post, 'medias_post': medias_post})


# ========== Supprimer: Post ===================
def delete_post(request, id):
    post = get_object_or_404(Post, id=id)
    medias_post = MediasPost.objects.filter(post=post).first()

    # Supprimez les fichiers associés au post (image et vidéo) s'ils existent
    if medias_post and medias_post.image and os.path.exists(medias_post.image.path):
        medias_post.image.delete()

    if post.video:
        # Ajoutez une pause pour laisser le temps au système de libérer le fichier
        time.sleep(1)
        
        # Supprimez le fichier vidéo s'il existe
        if os.path.exists(post.video.path):
            post.video.delete()

    # Supprimez le post
    post.delete()

    user_role = request.user.rôle  # Utilisez 'rôle' selon le modèle CustomUser
    if user_role == 'admin':
        return redirect('Ad_profile')
    elif user_role == 'personnel':
        return redirect('Per_profile')
    elif user_role == 'ecole':
        return redirect('Ec_profile')
    elif user_role == 'entreprise':
        return redirect('En_profile')


# Create your views here.
''' =========== Authentication ========= '''
def log_in(request):
    if request.method == 'POST':
        email = request.POST['email']  
        password = request.POST['password']

        user = authenticate(request, email=email, password=password)
        if user is not None and user.is_authenticated:
            login(request, user)

            roles_valides = ['admin','personnel', 'ecole', 'entreprise']

            if user.rôle == 'admin':
                # messages.error(request, "Vous n'avez pas la permission d'accéder à cette page.")
                return redirect('Ad_posts')
            elif user.rôle in roles_valides:
                if user.rôle == 'personnel':
                    return redirect('Per_posts')
                elif user.rôle == 'ecole':
                    return redirect('Ec_posts')
                elif user.rôle == 'entreprise':
                    return redirect('En_posts')
            else:
                messages.error(request, "Vous n'avez pas la permission d'accéder à cette page.")

    return render(request, 'auth/login.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        try:
            form.full_clean()  # Utilisez full_clean pour déclencher toutes les validations du formulaire
        except ValidationError as e:
            # Traitez les erreurs ici, puis ajoutez-les au contexte du formulaire
            for field, messages in e.message_dict.items():
                form.add_error(field, messages)
        if form.is_valid():
            user = form.save()
            user.backend = 'galsen.backends.EmailBackend'
            login(request, user)
            return redirect('profil')
    else:
        form = CustomUserCreationForm()

    return render(request, 'auth/register.html', {'form': form})

def profile(request):
    if request.method == 'POST':
        user = request.user
        # Récupérer les données du formulaire POST
        pays = request.POST.get('pays')
        ville = request.POST.get('ville')
        quartier = request.POST.get('quartier')
        langue = request.POST.get('langue')
        indicatif = request.POST.get('indicatif')
        phone = request.POST.get('phone')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        birthday = request.POST.get('birthday')

        # Mettre à jour les champs appropriés
        user.pays = pays
        user.ville = ville
        user.quartier = quartier
        user.langue = langue
        user.indicatif_pays = indicatif
        user.number_phone = phone
        user.first_name = firstname
        user.last_name = lastname
        user.birthday = birthday
        

        # Sauvegarder les modifications
        user.save()

        messages.success(request, 'Profil mis à jour avec succès.')

        # Rediriger vers la page du profil ou une autre page souhaitée
        return redirect('login')
    return render(request, 'auth/profils.html')

def log_out(request):
    # pass
    logout(request)
    messages.success(request, 'Deconexion')
    return redirect('login')

# ========== Formulaires Posts ===================
@role_required(['admin','personnel', 'ecole', 'entreprise'])
def create_post(request):
    if request.method == 'POST':
        contenu_post = request.POST.get('contenu_post')
        tag_post = request.POST.get('tag_post')
        categories = request.POST.get('categories')
        image_file = request.FILES.get('image')
        video = request.FILES.get('video')
        
        # Obtenez les informations de session actuelles
        session_info = obtenir_marque_dispositif(request)

        # Créez un nouveau post avec les informations de session
        new_post = Post.objects.create(
            user=request.user,
            contenu_post=contenu_post,
            categories=categories,
            tag_post=tag_post,
            video=video,
            session_info=session_info
        )

        if image_file:
            MediasPost.objects.create(
                post=new_post,
                image=image_file
            )
    
        user_role = request.user.rôle
        
        if user_role == 'admin':
            return redirect('Ad_posts')
        elif user_role == 'personnel':
            return redirect('Per_posts')
        elif user_role == 'ecole':
            return redirect('Ec_posts')
        elif user_role == 'entreprise':
            return redirect('En_posts')
    
    return render(request, 'formulaires/post.html')


@role_required(['admin','personnel', 'ecole', 'entreprise'])
def create_job(request):
    if request.method == 'POST':
        contenu_job = request.POST.get('contenu_job')
        title = request.POST.get('title')
    
        newJob = Job.objects.create(
            user=request.user,
            contenu_job=contenu_job, 
            title=title
            )
    
    
        user_role = request.user.rôle
        
        if user_role == 'admin':
            return redirect('Ad_posts')
        elif user_role == 'personnel':
            return redirect('Per_posts')
        elif user_role == 'ecole':
            return redirect('Ec_posts')
        elif user_role == 'entreprise':
            return redirect('En_posts')
        
    return render(request, 'formulaires/job.html')

@role_required(['admin','personnel', 'ecole', 'entreprise'])
def update(request):
    user_role = request.user.rôle

    # Charger le template de mise à jour correspondant au rôle de l'utilisateur
    if user_role == 'admin':
        return render(request, 'formulaires/update/admin_statut.html')
    elif user_role == 'personnel':
        return render(request, 'formulaires/update/personnel_statut.html')
    elif user_role == 'ecole':
        return render(request, 'formulaires/update/ecole_statut.html')
    elif user_role == 'entreprise':
        
        if request.method == 'POST':
            user = request.user

            # Récupérer les données du formulaire POST
            metier = request.POST.get('metier')
            pays = request.POST.get('pays')
            ville = request.POST.get('ville')
            quartier = request.POST.get('quartier')
            langue = request.POST.get('langue')
            indicatif = request.POST.get('indicatif')
            phone = request.POST.get('phone')

            # Mettre à jour les champs appropriés
            user.metier = metier
            user.pays = pays
            user.ville = ville
            user.quartier = quartier
            user.langue = langue
            user.indicatif_pays = indicatif
            user.number_phone = phone

            # Sauvegarder les modifications
            user.save()

            messages.success(request, 'Profil mis à jour avec succès.')

            # Rediriger vers la page du profil ou une autre page souhaitée
            return redirect('En_profile')
        return render(request, 'formulaires/update/entreprise_statut.html')

    # Gérer le cas d'erreur ou de rôle inconnu
    return render(request, 'path_vers_votre_template_d_erreur.html')

@role_required(['admin','personnel', 'ecole', 'entreprise'])
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        new_profile_image = request.FILES.get('image')

        # Supprimer l'ancienne image de la base de données et localement
        if user.profile_image:
            old_image_path = os.path.join(settings.MEDIA_ROOT, str(user.profile_image))
            os.remove(old_image_path)

        # Enregistrer la nouvelle image dans le répertoire de stockage local
        user.profile_image = new_profile_image
        user.save()

        user_role = request.user.rôle
        
        if user_role == 'admin':
            return redirect('Ad_profile')
        elif user_role == 'personnel':
            return redirect('Per_profile')
        elif user_role == 'ecole':
            return redirect('Ec_profile')
        elif user_role == 'entreprise':
            return redirect('En_profile')
        # Rediriger vers la page de profil ou toute autre page appropriée
    else:
        return render(request, 'formulaires/update/update_profile.html')

@role_required(['admin','personnel', 'ecole', 'entreprise'])
def update_banner(request):
    if request.method == 'POST':
        user = request.user
        new_profile_banner = request.FILES.get('banner')

        # Supprimer l'ancienne image de la base de données et localement
        if user.banner_image:
            old_image_path = os.path.join(settings.MEDIA_ROOT, str(user.banner_image))
            os.remove(old_image_path)

        # Enregistrer la nouvelle image dans le répertoire de stockage local
        user.banner_image = new_profile_banner
        user.save()

        user_role = request.user.rôle
        
        if user_role == 'admin':
            return redirect('Ad_profile')
        elif user_role == 'personnel':
            return redirect('Per_profile')
        elif user_role == 'ecole':
            return redirect('Ec_profile')
        elif user_role == 'entreprise':
            return redirect('En_profile')
        # Rediriger vers la page de profil ou toute autre page appropriée
    else:
        return render(request, 'formulaires/update/update_banner.html')
# ========== Profiles ===================
        # ========== Profiles personnels ===================
@role_required(['personnel'])
def Per_profile(request):
    CustomUser = request.user
    return render(request, 'Personnel/profiles/mon_profile/post.html', {'CustomUser': CustomUser})


# ========== Profiles Entreprises ===================
@role_required(['entreprise'])
def En_profile(request):
    CustomUser = request.user
    return render(request, 'Entreprise/profiles/mon_profile/post.html', {'CustomUser': CustomUser})

@role_required(['entreprise'])
def En_job(request):
    CustomUser = request.user
    return render(request, 'Entreprise/profiles/mon_profile/job.html', {'CustomUser': CustomUser})

@role_required(['entreprise'])
def En_Gestion_Boutique(request):
    if request.user.is_authenticated:
        try:
            # Récupère la boutique associée à l'utilisateur connecté
            user_boutique = Boutique.objects.get(user=request.user)
        except Boutique.DoesNotExist:
            # Gérer le cas où la boutique n'existe pas
            user_boutique = None

        # Maintenant, tu peux utiliser user_boutique dans ton contexte pour le rendre disponible dans ton template
        context = {'user_boutique': user_boutique}
        return render(request, 'Entreprise/profiles/mon_profile/boutique.html', context)

# ========== Profiles Ecole ===================
@role_required(['ecole'])
def Ec_profile(request):
    CustomUser = request.user
    return render(request, 'Ecole/profiles/mon_profile/post.html', {'CustomUser': CustomUser})

@role_required(['ecole'])
def Ec_job(request):
    CustomUser = request.user
    return render(request, 'Ecole/profiles/mon_profile/job.html', {'CustomUser': CustomUser})

# ========== Les commentaires Posts ===================
@role_required(['admin','personnel', 'ecole', 'entreprise'])
def post_comments(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Commentaire.objects.filter(post=post)
    return render(request, 'Commentaire/comment_post.html', {'post': post, 'comments': comments})

@role_required(['admin','personnel', 'ecole', 'entreprise'])
def submit_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        contenu_commentaire = request.POST.get('contenu_commentaire')
        image = request.FILES.get('image') if 'image' in request.FILES else None
        
        # Créez un nouvel objet Commentaire avec les données soumises
        commentaire = Commentaire.objects.create(post=post, user=request.user, contenu_commentaire=contenu_commentaire, image=image)
        
        # Redirigez l'utilisateur vers la même page ou une autre page appropriée
        return redirect('detail_post', post_id=post_id)
    
    # Gérer le cas où la méthode HTTP n'est pas POST
    return redirect('detail_post', post_id=post_id)


''' =========== personnels ========= '''
@role_required(['personnel'])
def Per_posts(request):
    # Récupérer tous les posts avec les médias associés, les utilisateurs, et la date de création
    posts = Post.objects.select_related('user').prefetch_related('mediaspost_set').order_by('-date_creation_post').all()

    # Mettre à jour le champ marque_dispositif dans le modèle CustomUser
    if request.user.is_authenticated:
        marque_dispositif = obtenir_marque_dispositif(request)
        request.user.marque_dispositif = marque_dispositif
        request.user.save()

    context = {
        'posts': posts,
    }
    return render(request, 'personnel/post.html', context)

@role_required(['personnel'])
def Per_ecole(request):
    CustomUsers = CustomUser.objects.filter(rôle='ecole')
    user = request.user
    
    context = {
        'CustomUsers': CustomUsers,
        'user': user
    }
    
    return render(request, 'personnel/ecole.html', context)

@role_required(['personnel'])
def Per_entreprise(request):
    CustomUsers = CustomUser.objects.filter(rôle='entreprise')
    user = request.user
    
    context = {
        'CustomUsers': CustomUsers,
        'user': user
    }
    
    return render(request, 'Personnel/entreprise.html', context)

@role_required(['personnel'])
def Per_job(request):
    jobs = Job.objects.select_related('user').order_by('-date_creation_post').all()
    user = request.user

    context = {
        'jobs': jobs,
        'user': user
    }
    
    return render(request, 'Personnel/job.html', context)

@role_required(['personnel'])
def Per_boutique(request):
    user = request.user

    context = {
        'user': user
    }
    
    return render(request, 'Personnel/boutique.html', context)


''' =========== Entreprises ========= '''
@role_required(['entreprise'])
def En_posts(request):
    # Récupérer tous les posts avec les médias associés, les utilisateurs, et la date de création
    posts = Post.objects.select_related('user').prefetch_related('mediaspost_set').order_by('-date_creation_post').all()
    user = request.user
    
    if request.user.is_authenticated:
        marque_dispositif = obtenir_marque_dispositif(request)
        request.user.marque_dispositif = marque_dispositif
        request.user.save()

    context = {
        'posts': posts,
        'user': user
    }

    return render(request, 'Entreprise/post.html', context)

@role_required(['entreprise'])
def En_personnel(request):
    CustomUsers = CustomUser.objects.filter(rôle='personnel')
    user = request.user
    
    context = {
        'CustomUsers': CustomUsers,
        'user': user
    }
    
    return render(request, 'Entreprise/personnel.html', context)

@role_required(['entreprise'])
def En_ecole(request):
    CustomUsers = CustomUser.objects.filter(rôle='ecole')
    user = request.user
    
    context = {
        'CustomUsers': CustomUsers,
        'user': user
    }
    
    return render(request, 'Entreprise/ecole.html', context)

@role_required(['entreprise'])
def En_boutique(request):
    user = request.user
    
    context = {
        'user': user
    }
    
    return render(request, 'Entreprise/boutique.html', context)


''' =========== Ecoles ========= '''
@role_required(['ecole'])
def Ec_posts(request):
    # Récupérer tous les posts avec les médias associés, les utilisateurs, et la date de création
    posts = Post.objects.select_related('user').prefetch_related('mediaspost_set').order_by('-date_creation_post').all()
    user = request.user
    
    if request.user.is_authenticated:
        marque_dispositif = obtenir_marque_dispositif(request)
        request.user.marque_dispositif = marque_dispositif
        request.user.save()

    context = {
        'posts': posts,
        'user': user
    }
    
    return render(request, 'Ecole/post.html', context)

@role_required(['ecole'])
def Ec_personnel(request):
    CustomUsers = CustomUser.objects.filter(rôle='personnel')
    user = request.user
    
    context = {
        'CustomUsers' : CustomUsers,
        'user' : user
    }
    
    return render(request, 'Ecole/personnel.html', context)

@role_required(['ecole'])
def Ec_entreprise(request):
    CustomUsers = CustomUser.objects.filter(rôle='entreprise')
    user = request.user
    
    context = {
        'CustomUsers' : CustomUsers,
        'user' : user
    }
    return render(request, 'Ecole/entreprise.html', context)

@role_required(['ecole'])
def Ec_boutique(request):
    user = request.user
    
    context = {
        'user' : user
    }
    return render(request, 'Ecole/boutique.html', context)


''' =========== Admins ========= '''
@role_required(['admin'])
def Ad_posts(request):
    # Récupérer tous les posts avec les médias associés, les utilisateurs, et la date de création
    posts = Post.objects.select_related('user').prefetch_related('mediaspost_set').order_by('-date_creation_post').all()
    user = request.user

    context = {
        'posts': posts,
        'user': user
    }
    
    return render(request, 'Admin/post.html', context)

@role_required(['admin'])
def Ad_personnel(request):
    user = request.user

    context = {
        'user': user
    }
    
    return render(request, 'Admin/personnel.html', context)

@role_required(['admin'])
def Ad_ecole(request):
    user = request.user

    context = {
        'user': user
    }
    
    return render(request, 'Admin/ecole.html', context)

@role_required(['admin'])
def Ad_entreprise(request):
    user = request.user

    context = {
        'user': user
    }
    return render(request, 'Admin/entreprise.html', context)

@role_required(['admin'])
def Ad_job(request):
    user = request.user

    context = {
        'user': user
    }
    
    return render(request, 'Admin/job.html', context)

@role_required(['admin'])
def Ad_boutique(request):
    user = request.user

    context = {
        'user': user
    }
    
    return render(request, 'Admin/boutique.html', context)
