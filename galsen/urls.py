from django.urls import path
# ========== Authentification ===================
from galsen.views import log_in, register, log_out

# ========== Formulaires Posts ===================
from galsen.views import create_post, create_job, create_even, create_product, a_propos

# ========== Profiles ===================
from galsen.views import Per_profile, En_profile, En_job, En_Gestion_Boutique, Ec_profile, Ec_job

# ========== Personnels ===================
from galsen.views import Per_posts, Per_ecole, Per_entreprise, Per_job, Per_boutique
# ========== Entreprises ===================
from galsen.views import En_posts, En_personnel, En_ecole, En_boutique
# ========== Ecoles ===================
from galsen.views import Ec_posts, Ec_personnel, Ec_entreprise, Ec_boutique
# ========== Admins ===================
from galsen.views import Ad_posts, Ad_personnel, Ad_ecole, Ad_entreprise, Ad_job, Ad_boutique

# ========== Details: Personnels, Entreprise, Ecole ===================
from galsen.views import PersonnelDetails, EcoleDetails, EntrepriseDetails, update_post

# ========== Update Statu: Personnels, Entreprise, Ecole ===================
from galsen.views import update, update_profile, update_banner, profile, boutique, update_logo_boutique, update_banner_boutique, update_description_boutique

# ========== Les Commentaires: Post et Les Réponses:Commentaires ===================
from galsen.views import post_comments, comment_responses

# ========== Les Followers: Les Likes ===================
from galsen.views import  AddDislike, AddLikes
# , RemoveFollower, SharedPosteVue, sharePoste, AddFollower

from . import views



urlpatterns = [
    # ========== A Propos ===================
    path('a_propos', a_propos, name = 'a_propos'),
    
    # ========== Les Followers: Les Commentaires ===================
    path('post/<int:post_id>/comments/', post_comments, name='post_comments'),
    path('comment/<int:comment_id>/responses/', comment_responses, name='comment_responses'),
    
    # ========== Les Followers: Les Likes, Les Shares ===================
    path('post/<int:pk>/like',AddLikes.as_view(),name='likes'),
    path('post/<int:pk>/dislike',AddDislike.as_view(),name='dislike'),
    
    # ========== Details: Profil, Personnels, Entreprise, Ecole, Boutique ===================
    path('personnel/<int:pk>/', PersonnelDetails.as_view(), name='personnel_details'),
    path('ecole/<int:pk>/', EcoleDetails.as_view(), name='ecole_details'),
    path('entreprise/<int:pk>/', EntrepriseDetails.as_view(), name='entreprise_details'),
    path('profiles/<int:pk>/', views.user_detail, name='user_detail'),
    path('a_propos/<int:user_id>/', views.a_propos_detail, name='a_propos_detail'),
     
    # ========== Update Statu, Update Profile, Update Banner, Update Post, Update Job: Personnels, Entreprise, Ecole ===================
    path('update', update, name = 'update'),
    path('update_profile', update_profile, name = 'update_profile'),
    path('update_banner', update_banner, name = 'update_banner'),
    path('update_post/<int:id>/', update_post, name='update_post'),
    path('update_logo_boutique', update_logo_boutique, name = 'update_logo_boutique'),
    path('update_banner_boutique', update_banner_boutique, name = 'update_banner_boutique'),
    path('update_description_boutique', update_description_boutique, name = 'update_description_boutique'),
    
    path('profil', profile, name = 'profil'),
    path('boutique', boutique, name = 'boutique'),

     
    # ========== Authentification ==================
    path('', log_in, name = 'login'),
    path('register', register, name = 'register'),
    path('logout', log_out, name = 'logout'),
    
    # ========== Formulaires Posts ===================
    path('post', create_post, name = 'post'),
    path('job', create_job, name = 'job'),
    path('even', create_even, name = 'even'),
    path('product', create_product, name = 'product'),
    
    # ========== Supprimer: Posts, Jobs, Product ===================
    path('delete_post/<int:id>/', views.delete_post, name='delete_post'),
    
    # ========== Profiles ===================
        # ========== Profiles Personnels ===================
    path('per_profile', Per_profile, name= 'Per_profile'),
    
        # ========== Profiles Entreprises ===================
    path('en_profile', En_profile, name= 'En_profile'),
    path('en_job', En_job, name= 'En_job'),
    path('en_Gestion_Boutique', En_Gestion_Boutique, name= 'En_Gestion_Boutique'),
    
            # ========== Profiles Ecole ===================
    path('ec_profile', Ec_profile, name= 'Ec_profile'),
    path('ec_job', Ec_job, name= 'Ec_job'),
    
    # =========== Personnels ================
                # ===== Les Pages =====
    path('per_post', Per_posts, name = 'Per_posts'),
    path('per_ecole', Per_ecole, name = 'Per_ecole'),
    path('per_entreprise', Per_entreprise, name = 'Per_entreprise'),
    path('per_job', Per_job, name = 'Per_job'),
    path('per_boutique', Per_boutique, name = 'Per_boutique'),
    
    # =========== Entreprises ================
                # ===== Les Pages =====
    path('en_post', En_posts, name = 'En_posts'),
    path('en_personnel', En_personnel, name = 'En_personnel'),
    path('en_ecole', En_ecole, name = 'En_ecole'),
    path('en_boutique', En_boutique, name = 'En_boutique'),
    
        # =========== Ecoles ================
                # ===== Les Pages =====
    path('ec_post', Ec_posts, name = 'Ec_posts'),
    path('ec_personnel', Ec_personnel, name = 'Ec_personnel'),
    path('ec_entreprise', Ec_entreprise, name = 'Ec_entreprise'),
    path('ec_boutique', Ec_boutique, name = 'Ec_boutique'),
    
    # =========== Admins ================
                # ===== Les Pages =====
    path('ad_post', Ad_posts, name = 'Ad_posts'),
    path('ad_personnel', Ad_personnel, name = 'Ad_Personnel'),
    path('ad_ecole', Ad_ecole, name = 'Ad_ecole'),
    path('ad_entreprise', Ad_entreprise, name = 'Ad_entreprise'),
    path('ad_job', Ad_job, name = 'Ad_job'),
    path('ad_boutique', Ad_boutique, name = 'Ad_boutique'),
]