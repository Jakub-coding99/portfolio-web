const div = document.querySelector(".prev-imgs")

const fileInput = document.querySelector(".file-input")
let files = []

fileInput.addEventListener("change", (event) => {
    files.push(...Array.from(event.target.files))
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
            let images = document.createElement("IMG")
            images.classList.add("img-preview")
            images.src = URL.createObjectURL(file)
            
            const previewWrapper = document.createElement("div")
            previewWrapper.classList.add("preview-wrapper")

            previewWrapper.appendChild(images)
            previewWrapper.appendChild(imgDescription)
            previewWrapper.appendChild(closeBtn)
            div.appendChild(previewWrapper)
            
            
            closeBtn.addEventListener("click",() => {
                files.splice(index,1)
                console.log(files)
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
    
   

    const response = await fetch("/admin-add_project", {
        "method":"POST",
        "body": formData,
    
    
    })

 const data = await response.json(); // <-- tady parsuješ JSON z Pythonu
if (data.redirect) {
    window.location.href = data.redirect; // redirect funguje
}
})



          


        
   

        
        

