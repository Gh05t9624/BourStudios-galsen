// Description
const voirPlus = document.getElementsByClassName('content-post');

    for (i = 0; i<voirPlus.length; i++) {
        voirPlus[i].addEventListener('click', function(){
            this.classList.toggle('actipe');
        })
    }

let video = document.querySelectorAll("video")
video.forEach(video => {
    let playPromise = video.play()
    if(playPromise !== undefined) {
        playPromise.then(() => {
            let observer = new IntersectionObserver(entries => {
                entries.forEach(entry => {
                    video.muted = true
                    if(entry.intersectionRatio !== 1 && !video.paused){
                        video.pause()
                    } else if (entry.intersectionRatio > 0.5 && video.paused) {
                        video.play()
                    }
                })
            }, {threshold: 0.5})
            observer.observe(video)
        })
    }
})

document.addEventListener('DOMContentLoaded', function () {
    var elementImageCount = document.getElementById('imageCount');
    var carouselImages = document.getElementById('imageCarousel');
    var totalImages = carouselImages.children.length;
    var indexImageActuelle = 1;
    
    // Mettre à jour le compte initial
    mettreAJourCompteImage();
    
    // Fonction pour mettre à jour le compte d'images
    function mettreAJourCompteImage() {
        elementImageCount.textContent = indexImageActuelle + '/' + totalImages + ' medias';
    }
    
    // Ajouter un gestionnaire de défilement pour le carrousel
    carouselImages.addEventListener('scroll', function () {
        var imageWidth = carouselImages.children[0].offsetWidth;
        var currentIndex = Math.ceil(carouselImages.scrollLeft / imageWidth) + 1;
    
        if (currentIndex !== indexImageActuelle && currentIndex <= totalImages) {
        indexImageActuelle = currentIndex;
        mettreAJourCompteImage();
        }
    });
    
    // Exemple de fonction pour passer à l'image suivante
    function nextImage() {
        var imageWidth = carouselImages.children[0].offsetWidth;
        var nextScrollLeft = carouselImages.scrollLeft + imageWidth;
    
        // Vérifier si le prochain défilement ne dépasse pas la largeur totale des images
        if (nextScrollLeft <= (totalImages - 1) * imageWidth) {
        carouselImages.scrollLeft = nextScrollLeft;
        }
    }
    
    // Exemple de fonction pour revenir à l'image précédente
    function prevImage() {
        var imageWidth = carouselImages.children[0].offsetWidth;
        var prevScrollLeft = carouselImages.scrollLeft - imageWidth;
    
        // Vérifier si le défilement précédent n'est pas inférieur à zéro
        if (prevScrollLeft >= 0) {
        carouselImages.scrollLeft = prevScrollLeft;
        }
    }
    });

// Like
$(document).ready(function() {
    $('.button-like').click(function(event) {
        event.preventDefault(); // Empêcher le comportement par défaut du formulaire
        
        var formId = $(this).closest('form').attr('id');
        var postId = formId.split('-')[2];
        var formData = $('#' + formId).serialize(); // Sérialiser les données du formulaire
        
        $.ajax({
            url: $('#' + formId).attr('action'),
            method: 'POST',
            data: formData,
            success: function(data) {
                // Mettez à jour l'interface utilisateur en fonction des données renvoyées par le serveur
                $('#likeIcon' + postId).html(data.like_icon);
                $('.number-like').html(data.like_count);
            }
        });
    });

    $('.button-dislike').click(function(event) {
        event.preventDefault(); // Empêcher le comportement par défaut du formulaire
        
        var formId = $(this).closest('form').attr('id');
        var postId = formId.split('-')[2];
        var formData = $('#' + formId).serialize(); // Sérialiser les données du formulaire
        
        $.ajax({
            url: $('#' + formId).attr('action'),
            method: 'POST',
            data: formData,
            success: function(data) {
                // Mettez à jour l'interface utilisateur en fonction des données renvoyées par le serveur
                $('#dislikeIcon' + postId).html(data.dislike_icon);
                $('.number-dislike').html(data.dislike_count);
            }
        });
    });
});


 // partage
document.addEventListener("DOMContentLoaded", function() {
    const shareButton = document.getElementById("shareButton");
    const popup = document.getElementById("popup");
    const closePopup = document.getElementById("closePopup");
  
    shareButton.addEventListener("click", function() {
      popup.style.display = "block";
    });
  
    closePopup.addEventListener("click", function() {
      popup.style.display = "none";
    });
  
    window.addEventListener("click", function(event) {
      if (event.target == popup) {
        popup.style.display = "none";
      }
    });
  });
  