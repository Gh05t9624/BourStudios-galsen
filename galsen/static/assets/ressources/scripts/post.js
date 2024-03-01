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

 // partage
 function shareToggle(parent_id) {
    const row = document.getElementById(parent_id);

    if (row.classList.contains('d-none')) {
        row.classList.remove('d-none');
    } else {
        row.classList.add('d-none');
    }
}

// Like Button