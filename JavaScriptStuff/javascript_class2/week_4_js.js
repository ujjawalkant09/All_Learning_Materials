
// Simple premitive types 
// function sum(a,b){
//     return a+b;
// }


// let a =1;
// let b = 2;


// let ans = sum(a,b)

// console.log(ans)



// Complex types 
// Code promise class itself (TODO)

// Classes In JavaScript 

// Class are used primmiry when we wants to attacthed the functionalty over variables 

class Shape{
    constructor(color){
        this.color = color;
    }

    paint(){
        console.log(`Painting with color ${this.color}`)
    }
}

class Rectangle extends Shape{
     constructor(width,height,color){
        super(color);
        this.width = width;
        this.height=height;
     }

    // Static methods
     static whoAMi(){
        console.log("I am rectanges");
     }

     area(){
        const area = this.width*this.height;
        return area;
     }

    //  paint(){
    //     console.log(`Painting with color ${this.color}`)
    //  }

}

class Circle extends Shape{
     constructor(radius,color){
        super(color)
        this.radius = radius;
        
     }

    // Static methods
     static whoAMi(){
        console.log("I am rectanges");
     }

     area(){
        const area = 3.14*this.radius*this.radius;
        return area;
     }

    //  paint(){
    //     console.log(`Painting with color ${this.color}`)
    //  }

}
class Square extends Shape{
     constructor(side,color){
        super(color);
        this.side = side;
     }

    // Static methods
     static whoAMi(){
        console.log("I am rectanges");
     }

     area(){
        const area = this.side*this.side;
        return area;
     }

    //  paint(){
    //     console.log(`Painting with color ${this.color}`)
    //  }

}





const rect = new Rectangle(2,4,"RED")


rect.paint()


// console.log(Rectangle.whoAMi())

// const d = new Date()

// console.log(d.getDate());