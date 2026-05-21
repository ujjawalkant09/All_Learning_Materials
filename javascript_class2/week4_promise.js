const fs = require("fs")

function fsReadFilePromisified(filePath,encoding){
    const p = new Promise((resolve,reject) =>{
        fs.readFile(filePath,encoding,(err,data)=>{
            if (err){
                reject(err);
            }else{
                setTimeout(()=>{
                 resolve(data);
                },1000)
                
            }
        })
    })

    return p;
}


function callback_1(data){
   console.log(`Success ${data}`);
   return data;
}

function callback_2(err){
    console.log(`Error ${err}`)
}

p = fsReadFilePromisified("class_3_week_3_web_development.txt","Utf-8").then(callback_1).catch(callback_2)

setInterval(()=>{
    console.log(p);
},500)



// Callback hell / promise chaining 


setTimeout(function () {
  console.log("hi");
  setTimeout(function () {
    console.log("hello");

    setTimeout(function () {
      console.log("hello there");
    }, 5000);
  }, 3000);
}, 1000);