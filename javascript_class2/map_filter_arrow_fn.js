
function sum2(a,b){
    return a+b;
}

// arraow function
const sum = (a,b) => {
    return a+b;
}

// MAP

// Giveb an array of numbers, return an array with each number multiplied by 2


const arr = [1,2,3,4,5,5];

// you can do it via loop but we will do it via map


// for(let i=0;i<arr.length;i++){
//     arr[i] = arr[i]*2;
// }

// console.log(arr)


// Map solution 

function transform(i){
   return i*2;
}


// const out = arr.map(transform)


const out = arr.map((i) =>{
    return i*2;
});


console.log(out);


// Filtering 

// give an input array , give me back all the even values from it.



const arr_1 = [1,2,3,4,5]

function even(i){
    if(i%2===0){
        return true;
    }
    return false;
}

const out_1 = arr_1.filter((i)=>{
    if(i%2===0){
        return true;
    }
    return false;
});

console.log(out_1);





// ------------------





