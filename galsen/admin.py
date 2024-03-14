from django.contrib import admin
from .models import CustomUser
from .models import Profil
from .models import Experience
from .models import Formation
from .models import Abonnement
from .models import Post
from .models import MediasPost
from .models import Commentaire
from .models import Like
from .models import Share
from .models import Reponse
from .models import Boutique
from .models import Product
from .models import MediasProduct
from .models import Job
from .models import ShareJob

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Profil)
admin.site.register(Experience)
admin.site.register(Formation)
admin.site.register(Abonnement)
admin.site.register(Post)
admin.site.register(MediasPost)
admin.site.register(Commentaire)
admin.site.register(Like)
admin.site.register(Share)
admin.site.register(Reponse)
admin.site.register(Boutique)
admin.site.register(Product)
admin.site.register(MediasProduct)
admin.site.register(Job)
admin.site.register(ShareJob)