const fs = require("fs")


// fs.readFile("a.txt","utf-8",callbackfunc)

function PromiseFileReading(path,encoding){
    let p = new Promise(function(resolve,reject){
        fs.readFile(path,encoding,function (err,data){
            if(err){
                reject(err,"more data");
            }else{
                resolve(data)
            }
        })
    });
    return p

}


function call_back_data(data){
    console.log(`Sucess :: ${data}`)
}


function call_back_data_2(err,extra){
    console.log(`Error ${err} :: ${extra}`)
}

PromiseFileReading("a1.txt","utf-8").then(call_back_data).catch(call_back_data_2)