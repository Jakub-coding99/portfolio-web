 let img_list = []
const sendIMG = async(url,formData) => {
        const response = await fetch(url, {
        "method":"POST",
        "body": formData,
    
    
    })

 const data = await response.json(); // <-- tady parsuješ JSON z Pythonu
if (data.redirect) {
    window.location.href = data.redirect; // redirect funguje
}


}


const div = document.querySelector(".prev-imgs")


const fileInput = document.querySelector(".file-input")
let files = []


fileInput.addEventListener("change", (event) => {
 


     const newFiles = Array.from(event.target.files).map(file => {
        // vytvoření nového souboru se změněným názvem
      
        return new File([file], `${Date.now()}_${file.name}`, { type: file.type });
    });
    
    
    files.push(...newFiles)
    fileInput.value = ""
    renderPreview()
})
    

   
let renderPreview = () => {
      div.innerHTML = ""
    if (files)
        
        {
        files.forEach((file,index) => {
            
           
            
        
            // BUTTON
            const closeBtn = document.createElement("p")
            closeBtn.classList.add("close-btn-img")
            closeBtn.textContent = "X"
            
            //image description
            let imgDescription = document.createElement("p")
            imgDescription.classList.add("img-descr")
            imgDescription.textContent = file["name"]
            

            //images
            let images = document.createElement("img")
            images.classList.add("img-preview")
            images.src = URL.createObjectURL(file)
            
            const previewWrapper = document.createElement("div")
            previewWrapper.classList.add("preview-wrapper")

            previewWrapper.appendChild(images)
            previewWrapper.appendChild(imgDescription)
            previewWrapper.appendChild(closeBtn)
            div.append(previewWrapper)
            
            
            
            closeBtn.addEventListener("click",() => {
                 files = files.filter(f => f !== file); 
            renderPreview(); 
                
                previewWrapper.remove()
               
                
    
            
                    
                    
                })

            //
           })
        }}
    
           
const form = document.querySelector(".project-form")
form.addEventListener("submit", async (event) => {
    event.preventDefault()
    
     


    
    const formData = new FormData();
    formData.append("title", event.target.title.value);
    formData.append("preview", event.target.preview.value);
    formData.append("description", event.target.description.value);

    // přidáme všechny soubory
    files.forEach(file => formData.append("files", file));
     for(let [key,value] of formData.entries())
        console.log(key,value)
    let endpoint = ""
    try {
        let choice = event.target.model.value
        
        if (choice === "Project"){
            endpoint = "/add/project"

        }

        if (choice === "Blog"){
            endpoint = "/add/blog"
        }



    }
    catch(TypeError) { 
        
        endpoint = form.dataset.endpoint
        
    }
    
    
    
 
   
    sendIMG(endpoint,formData)
           if(img_list.length > 0){
    await deleteImage(img_list, event.target.title.value);
}
   


})


const deleteImage = async (t,title) => {
    
    
    const response = await fetch("/check-img", {
        "method":"post",
        "body": JSON.stringify({"title":title,"images":t})
        
        

    })
    

}

const test = () => {
   
    const Images = document.querySelectorAll(".preview-wrapper")
    
    Images.forEach( img => {
        img.addEventListener("click", (event) => {
            let childs = img.children
            let childImg = childs[0].src
            let descr = childs[1]
            img_list.push(childImg)
            img.style.display = "none"
            
        })
       
        console.log(img_list)
    })
   
}


        
test()

        
        

