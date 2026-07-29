
function age_filter(arr_obj){
    let users = [];

    for(let i=0; i<arr_obj.length ; i++){
        console.log(i);
        console.log(arr_obj[i]);
        if(arr_obj[i].age > 18){
            users.push(arr_obj[i]);
        }
    }

    return users
    
}



const users = [
   {
    "user":"Ram",
    "age":17
   },
   {
    "user":"Ram",
    "age":18
   },{
    "user":"Ram",
    "age":19
   },{
    "user":"Ram",
    "age":20
   },{
    "user":"Ram",
    "age":21
   }
]

out = age_filter(users)

console.log(out)