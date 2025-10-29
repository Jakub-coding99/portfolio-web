
console.log("vse ok")

const fileInput = document.querySelector(".file-input")
fileInput.addEventListener("change", (event) => {
    files = event.target.files
    for(file of files){
        console.log(file["name"])
    }})
    
   
    
