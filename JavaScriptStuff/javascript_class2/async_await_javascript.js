const fs = require("fs")


function fsReadFilePromisified(filePath,encoding){
    let p = new Promise(function(resolve,reject){
        fs.readFile(filePath,encoding,function(err,data){
            if(err){
                reject(err);
            }else{
                resolve(data);
            }
        })
    });
    return p
}



async function main(){
try{
        let file1Contents = await fsReadFilePromisified("a1.txt","utf-8");
        console.log(file1Contents);
    }catch(e){
    console.log("error in file reading ");
    }
}


main()