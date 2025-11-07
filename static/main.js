let navMenu = document.querySelector(".nav-menu")
let hamburger = document.querySelector(".hamburger")

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
   
    if (i === t.length){
        let bracket = document.querySelector(".bracket")
        bracket.classList.toggle("on")
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
    
    



mottoWriter()

document.addEventListener("scroll", (event) => {
    
    
    
    if (scrollY > 350) {
        document.querySelector(".arrow").classList.add("on")

    }
    else {
        document.querySelector(".arrow").classList.remove("on")

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

    let project = document.querySelectorAll(".project")
    project.forEach(el => observer.observe(el))

    about = document.querySelector(".container-about")
    observer.observe(about)


    descText = document.querySelector(".about-text")
    console.log(descText)
    observer.observe(descText)


}

animateFunc()



