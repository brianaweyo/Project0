let arrow = document.querySelectorAll(" .arrow");
for (var i = 0; i<arrow.length; i++){
     arrow[i].addEventListener("click",(e)=>{    
    let arrowParent = e.target.parentElement.parentElement;
    console.log(arrowParent);
    arrowParent.classList.toggle("showMenu");
    });

}
let sidebar =document.querySelectorAll(".sidebar");
let sidebarBtn =document.querySelectorAll(".bx-menu");
console.log(sidebarBtn);
sidebarBtn.addEventListener("click", ()=>{
  sidebar.classList.toggle("close");
});