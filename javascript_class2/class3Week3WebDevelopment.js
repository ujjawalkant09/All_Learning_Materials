
// const fs = require("fs");

// function fileReadCallback(err, data){
//     if(err){
//         console.log("Error in reading file");
//         return;
//     }
//     console.log(data);
//     console.log(data);
//     console.log(data);
//     console.log(data);

// }

// fs.readFile("class_3_week_3_web_development.txt", "utf-8",fileReadCallback);

// console.log(contents);

// let s=0;
// for(let i=0;i<100;i++){
//     s+=i;
//     console.log(s);
// }



// function sum(a,b){
//     return a+b;
// }

// function sub(a,b){
//     return a-b;
// }

// function doArithmatic(a,b,fn){
//     return fn(a,b);
// }



// const a = 1;
// const b = 2;

// console.log(a)
// console.log(b)

// function callBack(){
//     console.log(a+b)
// }   

// setTimeout(callBack,1000)

// console.log(a+b)



// function callback(){
//     console.log("hello callback called");
// }

// setInterval(callback,1000);
// // setTimeout(callback,2000);
// // setTimeout(callback,3000);

// let x = 0;
// for(let i=0;i<10;i++){
//     x+=i;
// }

// console.log(x)


// SetTimeout and SetInterval are used to schedule tasks to be executed after a certain delay or at regular intervals, respectively. They allow you to perform asynchronous operations without blocking the main thread of execution.

// setTimeout(callback, delay) schedules the callback function to be executed once after the specified delay (in milliseconds). For example:

// setTimeout(() => {
//     console.log("This will be printed after 2 seconds");
// }, 2000);

// setInterval(callback, interval) schedules the callback function to be executed repeatedly at the specified interval (in milliseconds). For example:

// setInterval(() => {
//     console.log("This will be printed every 3 seconds");
// }, 3000);

// Both setTimeout and setInterval return a unique identifier that can be used to cancel the scheduled task using clearTimeout or clearInterval, respectively. For example:

// const timeoutId = setTimeout(() => {
//     console.log("This will not be printed");
// }, 2000);

// clearTimeout(timeoutId);

// const intervalId = setInterval(() => {
//     console.log("This will not be printed");
// }, 3000);

// clearInterval(intervalId);   