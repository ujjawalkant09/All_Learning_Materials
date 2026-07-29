const obj = {
    name:"Alice",
    age:23,
    SayHello:function(){
        return "Hello"
    },
    carrer:{}
}


// console.log(Object.values(obj))

// console.log(Object.keys(obj))

// for (let key in obj){
//     console.log(key)
// }


const obj2 = {
    hairColor:"black",
    arr:[1,2,3]

}

const obj3 = {...obj,...obj2}

obj3.carrer.info = "tech"

// console.log(obj3)

const {hairColor,name} = obj3

// console.log(hairColor,name)

const multiply = function(a,b){
    return a*b 
}

mul = multiply(3,5)
// console.log(mul)

let map = new Map()
map.set('name',"test")
map.set('age',25)

// console.log(map)

// let set = new Set()

// set.add(1)
// set.add(2)
// set.add(2)
// set.add(3)
// set.add(4)
// set.add(4)

// console.log(set)

// set.delete(2)

// console.log(set)


let num = 6

for(var i=0;i<num;i++){
    console.log(i)
}