const showImage = () => {
    let imgPreview = document.querySelector(".project-img-preview")
    const allImages = document.querySelectorAll(".project-images")
    const modal = document.querySelector(".modal")
    
    
    
    const closeButton = document.querySelector(".close-modal-btn")
    const modalImg = document.querySelector(".modal-img")

     const next = document.querySelector(".next")
    const prev = document.querySelector(".prev")

    
    let img_index = 0
    
    imgPreview.innerHTML = `<img src="${allImages[0].src}" alt="">`;
    

    allImages.forEach((element, index) => {
        element.addEventListener("click", () => {
            img_index = index;
            imgPreview.innerHTML = `<img src="${allImages[img_index].src}" alt="">`;
        });
    });


    imgPreview.addEventListener("click", (event) => {
        
        modal.style.display = "flex"
          modalImg.innerHTML = `<img src="${allImages[img_index].src}" alt="Galerie obrázků">`;
        

       

       
        
        
    })

    closeButton.addEventListener("click", () => {
        modal.style.display = "none"
        modalImg.innerHTML = ""
        
    })

    next.addEventListener("click", (event) => {
            img_index = (img_index + 1) % allImages.length
           
            modalImg.querySelector("img").src = allImages[img_index].src

        })
   
    prev.addEventListener("click", (event) => {
        img_index = (img_index - 1 + allImages.length) % allImages.length
        modalImg.querySelector("img").src = allImages[img_index].src

    })

    

   

    




    
    
}

showImage()

