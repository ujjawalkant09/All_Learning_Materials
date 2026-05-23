
// Callback examples 

// const { rejects } = require("node:assert");
// const { resolve } = require("node:dns");

const fs = require("fs")

// fs.readFile("a.txt","utf-8",function(err,data){
//     if (err){
//         console.log("error while reading the files");
//     }else{
//         console.log(`Sucesss ${data}`)
//     }
// })

/*

Promise has three states 
1. Pending  -> the operation is still running 
2. fulfilled(Resolved) -> The operation completed successfully 
3.Rejected  -> The operation failed 

Once fulfilled or rejected, the promise is settled and cannot changes state

*/



/*

const p = new Promise((res,reject) => res);

console.log(p)

*/





function fsReadFilePromisified(fileName,encoding){
    let p = new Promise(function(resolve,rejects){
        fs.readFile(fileName,encoding,function(err,data){
            if(err){
                rejects(err);
            }else{
                resolve(data);
            }

        })
    });
    return p
}

// fsReadFilePromisified("a.txt","utf-8").then(function(data){console.log(data)}).catch(function(err){console.log(err)})

 

function setTimeoutPromisified(delay){
    let p = new Promise(function(resolve,reject){
        setTimeout(function(){
            resolve()
        },delay)

    });
    return p;
}


function callback_test(){
    console.log("Test 2")
}

// setTimeout(callback_test,100)

setTimeoutPromisified(100).then(callback_test)