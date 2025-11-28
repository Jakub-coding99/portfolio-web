// window.addEventListener("load" , () => {
    


//     const navType = performance.getEntriesByType("navigation")[0].type;

//     if (navType === "reload") {
       
//         document.querySelector(".loader").style.display = "none"
//         return
//     }
//     const loaderEl = document.querySelector(".loader")
//     loaderEl.style.opacity = "0"
//     loaderEl.style.visibility = "hidden"
//     loaderEl.addEventListener("transitionend", () => {
        
//         document.body.removeChild(loaderEl)
//     })
// })




const navMenu = document.querySelector(".nav-menu")
const hamburger = document.querySelector(".hamburger")


hamburger.addEventListener("click",() => {
    hamburger.classList.toggle("active")
    navMenu.classList.toggle("active")

   
    


})


document.querySelectorAll(".nav-link").forEach( n =>   n.addEventListener("click",() => {
    hamburger.classList.remove("active")
    navMenu.classList.remove("active")


})





)



let textWriter =  (el,t,i = 0) => {
    if ( document.querySelector(".bracket")) {
         if (i === t.length){
        let bracket = document.querySelector(".bracket")
        bracket.classList.toggle("on")
        return
    }

        
    }

    else {
        return
    }
   
   

    
    el.textContent += t[i]




    setTimeout(() => textWriter(el,text,i + 1),220)

   
    

}
let text = "Python Developer"
let element = document.querySelector(".job-span")

textWriter(element,text)

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}



async function mottoWriter()  {

    if (document.querySelector(".new-motto")) {

         let writeMotto = document.querySelector(".new-motto")

   
    
    const motto = ['"Každá chyba je krok blíž k řešení"','"Každý projekt je krok vpřed"','"Cíl? Růst s každým řádkem"']
    
    while (true) {
        
        for (let m of motto) {
        
       
        
        writeMotto.textContent = m
        writeMotto.classList.add("on")
         await sleep(500)
        
        
        
        
        await sleep(5000)
        writeMotto.classList.remove("on")
         await sleep(500)


        }
        
        
        
        
    }



    }

    else {
        return
    }
   


    }
    
    



mottoWriter()

document.addEventListener("scroll", (event) => {
    
    if (document.querySelector(".arrow")) {
          if (scrollY > 350) {
        document.querySelector(".arrow").classList.add("on")

    }
    else {
        document.querySelector(".arrow").classList.remove("on")

    }


    }
    else {
        return
    }
    
  
})



let animateFunc = () => {
   
    options = {
        root: null,
        rootMargin: "0px",
        threshold: 0.3
    }

    let callback = (entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.classList.contains("activated")){
                entry.target.classList.add("activated")
            }
        })
    }

    const observer = new IntersectionObserver(callback,options)

    if (document.querySelectorAll(".project")) {
          let project = document.querySelectorAll(".project")
        project.forEach(el => observer.observe(el))

    }

  

    if (document.querySelector(".container-about")){
        let about = document.querySelector(".container-about")
        observer.observe(about)

    }

    if (document.querySelector(".about-text")) {
        let descText = document.querySelector(".about-text")
        observer.observe(descText)

    }


   if (document.querySelectorAll(".blog-item")) {
        let blogPosts = document.querySelectorAll(".blog-item")
        
        blogPosts.forEach(el => observer.observe(el))
       

   }

    


}

animateFunc()


if (document.querySelector("#form-contact")) {
   const contactForm = document.querySelector("#form-contact")
contactForm.addEventListener("submit",async (e) => {
    const toast = document.querySelector(".toast")
    toast.classList.remove("activated")
    
    e.preventDefault()
    let email = e.target.email.value
    let name = e.target.name.value
    let msg = e.target.msg.value
    let contactData = {"email":email,"name":name,"msg":msg}
    
    const response = await fetch("/submit_contact",{
        "method":"post",
        "headers": {
            "Content-Type": "application/json"},
        "body":JSON.stringify(contactData)

        }
    )

    e.target.email.value = ""
    e.target.name.value = ""
    e.target.msg.value = ""

    
    toast.classList.add("activated")
    
    const closeToast = toast.querySelector(".close-toast")
    closeToast.addEventListener("click", () => {
        toast.classList.remove("activated")
    })

        


})

}
