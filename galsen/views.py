from django.http import HttpResponse
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
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

from .models import CustomUser, Post, MediasPost, Job, Boutique, Commentaire, Reponse, Product, MediasProduct, Profil, Experience, Formation
from django.views.generic import DetailView, View
from galsen.utils import obtenir_marque_dispositif
from django.http import JsonResponse
from django.db.models import Q


# ========== Details: profil, A propos ===================
def user_detail(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    context = {}

    
    if user.rôle == 'personnel':
        template_name = 'profiles/id/personnel.html'
        context['personnel'] = user
    elif user.rôle == 'entreprise':
        template_name = 'profiles/id/entreprise.html'
        context['entreprise'] = user
    elif user.rôle == 'ecole':
        template_name = 'profiles/id/ecole.html'
        context['ecole'] = user
    
    return render(request, template_name, context)

# break

def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

def a_propos_detail(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    context = {'user': user}
    
    if user.rôle == 'personnel':
        template_name = 'profiles/id/A_propos/cv_personnel.html'
        context['profil'] = get_or_none(Profil, user=user)
        context['experience'] = get_or_none(Experience, user=user)
        context['formation'] = get_or_none(Formation, user=user)
    elif user.rôle == 'entreprise':
        template_name = 'profiles/id/A_propos/propos_entreprise.html'
        # Ajoutez les données spécifiques à l'entreprise au besoin
    elif user.rôle == 'ecole':
        template_name = 'profiles/id/A_propos/propos_ecole.html'
        # Ajoutez les données spécifiques à l'école au besoin
    else:
        # Gérer le cas où le rôle n'est pas reconnu
        template_name = 'profiles/id/A_propos/default.html'
    
    return render(request, template_name, context)


# ========== Details: personnels ===================
class PersonnelDetails(DetailView):
    model = CustomUser
    template_name = 'profiles/id/personnel.html'
    context_object_name = 'personnel'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print("Contexte de la vue détaillée :", context)
        return context
# break   

# ========== Details: Ecole ===================
class EcoleDetails(DetailView):
    model = CustomUser
    template_name = 'profiles/id/ecole.html'
    context_object_name = 'ecole'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print("Contexte de la vue détaillée :", context)
        return context  
    
# ========== Details: Entreprise ===================
class EntrepriseDetails(DetailView):
    model = CustomUser
    template_name = 'profiles/id/entreprise.html'
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
        post.contenu_post = request.POST['contenu_post']
        post.tag_post = request.POST['tag_post']
        post.save()

        new_image_file = request.FILES.get('image')
        new_video_file = request.FILES.get('video')

        if medias_post and medias_post.image and os.path.exists(medias_post.image.path):
            medias_post.image.delete(save=False)

        if post.video and os.path.exists(post.video.path):
            post.video.delete(save=False)

        if new_video_file:
            post.video = new_video_file
        post.save()

        if medias_post:
            if new_image_file:
                medias_post.image = new_image_file
            medias_post.save()
        else:
            if new_image_file:
                MediasPost.objects.create(post=post, image=new_image_file)

        user_role = request.user.rôle  
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

    if medias_post and medias_post.image and os.path.exists(medias_post.image.path):
        medias_post.image.delete()

    if post.video:
        # Ajoutez une pause pour laisser le temps au système de libérer le fichier
        time.sleep(1)
        
        if os.path.exists(post.video.path):
            post.video.delete()

    post.delete()

    user_role = request.user.rôle
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
        

        user.save()

        messages.success(request, 'Profil mis à jour avec succès.')

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

# ========== Formulaires Even ===================
@role_required(['admin', 'ecole', 'entreprise'])
def create_even(request):
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
    
    return render(request, 'formulaires/even.html')

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
def create_product(request):
    if request.method == 'POST':
        # Récupérer les données du formulaire
        description = request.POST.get('description')
        nom_produit = request.POST.get('nom_produit')
        prix = request.POST.get('prix')
        video = request.FILES.get('video')
        image = request.FILES.get('image')
        
        # Récupérer l'utilisateur actuel
        utilisateur = request.user
        
        # Récupérer la boutique associée à l'utilisateur actuel
        boutique = Boutique.objects.get(user=utilisateur)
        
        # Créer un nouveau produit
        new_product = Product.objects.create(
            boutique=boutique,
            description=description,
            nom_produit=nom_produit,
            prix=prix,
            video=video
        )
        
        # Si une image est fournie, créer un objet MediasProduct correspondant
        if image:
            MediasProduct.objects.create(
                produit=new_product,
                image=image
            )
        
        # Rediriger l'utilisateur vers une autre page après la création du produit
        return redirect('En_Gestion_Boutique')
        
    return render(request, 'formulaires/product.html')

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

            
            user.save()

            messages.success(request, 'Profil mis à jour avec succès.')

            
            return redirect('En_profile')
        return render(request, 'formulaires/update/entreprise_statut.html')

    
    return render(request, 'path_vers_votre_template_d_erreur.html')

@role_required(['admin','personnel', 'ecole', 'entreprise'])
def a_propos(request):
    user_role = request.user.rôle
    
    # Charger le template de mise à jour correspondant au rôle de l'utilisateur
    if user_role == 'personnel':
        return render(request, 'profiles/A_Propos/cv_personnel.html')
    elif user_role == 'ecole':
        return render(request, 'profiles/A_Propos/propos_ecole.html')
    elif user_role == 'entreprise':
        return render(request, 'profiles/A_Propos/propos_entreprise.html')

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
        # Rediriger vers la page de profil appropriée
    else:
        return render(request, 'formulaires/update/update_profile.html')
    
# break

# Update logo Boutique
def update_logo_boutique(request):
    if request.method == 'POST':
        # Récupérer l'utilisateur actuellement connecté
        user = request.user

        # Récupérer la boutique associée à cet utilisateur
        boutique = Boutique.objects.get(user=user)

        # Récupérer l'image du formulaire
        image = request.FILES.get('image')

        # Mettre à jour la photo de profil de la boutique
        if image:
            # Supprimer l'ancienne image de la base de données et localement
            if boutique.photo_profil:
                old_image_path = boutique.photo_profil.path
                boutique.photo_profil.delete(save=False)

            # Enregistrer la nouvelle image dans la base de données
            boutique.photo_profil = image
            boutique.save()

        # Rediriger vers une page de confirmation ou une autre vue
        return redirect('En_Gestion_Boutique')

    # Si la méthode de requête est GET, simplement renvoyer le formulaire HTML
    return render(request, 'formulaires/update/update_logo_boutique.html')
# break

# Update Banner Boutique
def update_banner_boutique(request):
    if request.method == 'POST':
        # Récupérer l'utilisateur actuellement connecté
        user = request.user

        # Récupérer la boutique associée à cet utilisateur
        boutique = Boutique.objects.get(user=user)

        # Récupérer l'image du formulaire
        image = request.FILES.get('image')

        # Mettre à jour la photo de profil de la boutique
        if image:
            # Supprimer l'ancienne image de la base de données et localement
            if boutique.banner_image:
                old_image_path = boutique.banner_image.path
                boutique.banner_image.delete(save=False)

            # Enregistrer la nouvelle image dans la base de données
            boutique.banner_image = image
            boutique.save()

        # Rediriger vers une page de confirmation ou une autre vue
        return redirect('En_Gestion_Boutique')

    # Si la méthode de requête est GET, simplement renvoyer le formulaire HTML
    return render(request, 'formulaires/update/update_banner_boutique.html')
# break

# Update Description Boutique
def update_description_boutique(request):
    if request.method == 'POST':
        # Récupérer l'utilisateur actuellement connecté
        user = request.user

        # Récupérer la boutique associée à cet utilisateur
        boutique = Boutique.objects.get(user=user)

        
        description = request.POST.get('description')

        

            # Enregistrer la nouvelle image dans la base de données
        boutique.description = description
        boutique.save()

        # Rediriger vers une page de confirmation ou une autre vue
        return redirect('En_Gestion_Boutique')

    # Si la méthode de requête est GET, simplement renvoyer le formulaire HTML
    return render(request, 'formulaires/update/update_description_boutique.html')
# break

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
    return render(request, 'profiles/mon_profile/personnel.html', {'CustomUser': CustomUser})
# ========== Break ===================

        # ========== Profiles Entreprises ===================
@role_required(['entreprise'])
def En_profile(request):
    CustomUser = request.user
    return render(request, 'profiles/mon_profile/entreprise_post.html', {'CustomUser': CustomUser})

@role_required(['entreprise'])
def En_job(request):
    CustomUser = request.user
    return render(request, 'profiles/mon_profile/entreprise_job.html', {'CustomUser': CustomUser})

@role_required(['entreprise'])
def En_Gestion_Boutique(request):
    try:
        # Récupère la boutique associée à l'utilisateur connecté
        user_boutique = Boutique.objects.get(user=request.user)
        
        # Récupérer les produits associés à cette boutique
        produits = user_boutique.product_set.all()
        
    except Boutique.DoesNotExist:
        # Redirige vers la page 'auth/boutique.html' si la boutique n'existe pas
        return render(request, 'auth/boutique.html')

    # Maintenant, tu peux utiliser user_boutique et produits dans ton contexte pour le rendre disponible dans ton template
    context = {
        'user_boutique': user_boutique,
        'produits': produits
    }
    return render(request, 'profiles/mon_profile/boutique.html', context)
# Break

def boutique(request):
    if request.method == 'POST':
        # Récupère l'utilisateur connecté
        user = request.user
        
        # Récupère les données du formulaire
        nom_boutique = request.POST.get('nom_boutique')
        devise_boutique = request.POST.get('devise_boutique')
        
        # Crée un nouvel objet Boutique
        nouvelle_boutique = Boutique.objects.create(
            user=user,
            nom_boutique=nom_boutique,
            devise_boutique=devise_boutique
        )
        
        # Redirige vers la vue pour gérer la boutique
        return redirect('En_Gestion_Boutique')
        
    return render(request, 'auth/boutique.html')
# break

        # ========== Profiles Ecole ===================
@role_required(['ecole'])
def Ec_profile(request):
    CustomUser = request.user
    return render(request, 'profiles/mon_profile/ecole_post.html', {'CustomUser': CustomUser})

@role_required(['ecole'])
def Ec_job(request):
    CustomUser = request.user
    return render(request, 'profiles/mon_profile/ecole_job.html', {'CustomUser': CustomUser})

# ========== Les commentaires: Posts ===================
@role_required(['admin','personnel', 'ecole', 'entreprise'])
def post_comments(request, post_id):
    
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)  # Utilisation de id=post_id pour récupérer le post
        contenu_commentaire = request.POST.get('contenu_commentaire')
        image = request.FILES.get('image')
        
        # Créez un nouvel objet Commentaire avec les données soumises
        commentaire = Commentaire.objects.create(post=post, user=request.user, contenu_commentaire=contenu_commentaire, image=image)
        
        # Redirigez l'utilisateur vers la même page ou une autre page appropriée
        #return redirect('detail_post', post_id=post_id)
    
    post = get_object_or_404(Post, id=post_id)
    comments = Commentaire.objects.filter(post=post)
    return render(request, 'Commentaire/comment_post.html', {'post': post, 'comments': comments})

# ========== Les Réponses: Commentaires ===================
@role_required(['admin','personnel', 'ecole', 'entreprise'])
def comment_responses(request, comment_id):
    
    if request.method == 'POST':
        comment = get_object_or_404(Commentaire, id=comment_id)
        contenu_text = request.POST.get('contenu_text')
        image = request.FILES.get('image')
        
        reponse = Reponse.objects.create(commentaire=comment, user=request.user, contenu_text=contenu_text, image=image)
    
    comment = get_object_or_404(Commentaire, id=comment_id)
    responses = Reponse.objects.filter(commentaire_id=comment.id)
    return render(request, 'Commentaire/response.html', {'comment': comment, 'responses': responses})

# ========== Les Followers: Les Likes, Les Dislikes, Les Shares ===================
class AddLikes(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)

        # Vérifier si l'utilisateur a déjà aimé ou n'aime pas le poste
        is_dislike = post.dislike.filter(pk=request.user.pk).exists()
        is_like = post.like_post.filter(pk=request.user.pk).exists()

        # Si l'utilisateur n'aime pas le poste, le retirer de la liste des dislikes
        if is_dislike:
            post.dislike.remove(request.user)

        # Si l'utilisateur n'a pas déjà aimé le poste, l'ajouter aux likes
        if not is_like:
            post.like_post.add(request.user)
            like_icon = '<i class="fa fa-thumbs-up primary"></i>'
        # Si l'utilisateur a déjà aimé le poste, le retirer des likes
        else:
            post.like_post.remove(request.user)
            like_icon = '<i class="fa fa-thumbs-up"></i>'

        # Renvoyer les informations mises à jour
        response_data = {
            'like_count': post.like_post.count(),
            'like_icon': like_icon,
        }
        
class AddFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = get_object_or_404(CustomUser, pk=pk)
        profile.followers.add(request.user)
        return JsonResponse({'success': True})

class RemoveFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = get_object_or_404(CustomUser, pk=pk)
        profile.followers.remove(request.user)
        return JsonResponse({'success': True})

class AddDislike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)

        # Vérifier si l'utilisateur a déjà aimé ou n'aime pas le poste
        is_like = post.like_post.filter(pk=request.user.pk).exists()
        is_dislike = post.dislike.filter(pk=request.user.pk).exists()

        # Si l'utilisateur a déjà aimé le poste, le retirer de la liste des likes
        if is_like:
            post.like_post.remove(request.user)

        # Si l'utilisateur n'a pas déjà détesté le poste, l'ajouter aux dislikes
        if not is_dislike:
            post.dislike.add(request.user)
            dislike_icon = '<i class="fa fa-thumbs-down primary"></i>'
        # Si l'utilisateur a déjà détesté le poste, le retirer des dislikes
        else:
            post.dislike.remove(request.user)
            dislike_icon = '<i class="fa fa-thumbs-down"></i>'

        # Renvoyer les informations mises à jour
        response_data = {
            'dislike_count': post.dislike.count(),
            'dislike_icon': dislike_icon,
        }
        
        # Retourner une réponse JSON
        
    
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
    return render(request, 'users/personnel/post.html', context)

@role_required(['personnel'])
def Per_ecole(request):
    CustomUsers = CustomUser.objects.filter(rôle='ecole')
    user = request.user
    
    context = {
        'CustomUsers': CustomUsers,
        'user': user
    }
    
    return render(request, 'users/personnel/ecole.html', context)

@role_required(['personnel'])
def Per_entreprise(request):
    CustomUsers = CustomUser.objects.filter(rôle='entreprise')
    user = request.user
    
    context = {
        'CustomUsers': CustomUsers,
        'user': user
    }
    
    return render(request, 'users/Personnel/entreprise.html', context)

@role_required(['personnel'])
def Per_job(request):
    jobs = Job.objects.select_related('user').order_by('-date_creation_post').all()
    user = request.user

    context = {
        'jobs': jobs,
        'user': user
    }
    
    return render(request, 'users/Personnel/job.html', context)

@role_required(['personnel'])
def Per_boutique(request):
    produits = Product.objects.select_related('boutique').order_by('-date_creation').all()
    user = request.user

    context = {
        'user': user,
        'produits': produits
    }
    
    return render(request, 'users/Personnel/boutique.html', context)


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

    return render(request, 'users/Entreprise/post.html', context)

@role_required(['entreprise'])
def En_personnel(request):
    CustomUsers = CustomUser.objects.filter(rôle='personnel')
    user = request.user
    
    context = {
        'CustomUsers': CustomUsers,
        'user': user
    }
    
    return render(request, 'users/Entreprise/personnel.html', context)

@role_required(['entreprise'])
def En_ecole(request):
    CustomUsers = CustomUser.objects.filter(rôle='ecole')
    user = request.user
    
    context = {
        'CustomUsers': CustomUsers,
        'user': user
    }
    
    return render(request, 'users/Entreprise/ecole.html', context)

@role_required(['entreprise'])
def En_boutique(request):
    produits = Product.objects.select_related('boutique').order_by('-date_creation').all()
    user = request.user

    context = {
        'user': user,
        'produits': produits
    }
    return render(request, 'users/Entreprise/boutique.html', context)


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
    
    return render(request, 'users/Ecole/post.html', context)

@role_required(['ecole'])
def Ec_personnel(request):
    CustomUsers = CustomUser.objects.filter(rôle='personnel')
    user = request.user
    
    context = {
        'CustomUsers' : CustomUsers,
        'user' : user
    }
    
    return render(request, 'users/Ecole/personnel.html', context)

@role_required(['ecole'])
def Ec_entreprise(request):
    CustomUsers = CustomUser.objects.filter(rôle='entreprise')
    user = request.user
    
    context = {
        'CustomUsers' : CustomUsers,
        'user' : user
    }
    return render(request, 'users/Ecole/entreprise.html', context)

@role_required(['ecole'])
def Ec_boutique(request):
    produits = Product.objects.select_related('boutique').order_by('-date_creation').all()
    user = request.user

    context = {
        'user': user,
        'produits': produits
    }
    return render(request, 'users/Ecole/boutique.html', context)


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
    
    return render(request, 'users/Admin/post.html', context)

@role_required(['admin'])
def Ad_personnel(request):
    user = request.user

    context = {
        'user': user
    }
    
    return render(request, 'users/Admin/personnel.html', context)

@role_required(['admin'])
def Ad_ecole(request):
    user = request.user

    context = {
        'user': user
    }
    
    return render(request, 'users/Admin/ecole.html', context)

@role_required(['admin'])
def Ad_entreprise(request):
    user = request.user

    context = {
        'user': user
    }
    return render(request, 'users/Admin/entreprise.html', context)

@role_required(['admin'])
def Ad_job(request):
    user = request.user

    context = {
        'user': user
    }
    
    return render(request, 'users/Admin/job.html', context)

@role_required(['admin'])
def Ad_boutique(request):
    user = request.user

    context = {
        'user': user
    }
    
    return render(request, 'users/Admin/boutique.html', context)
