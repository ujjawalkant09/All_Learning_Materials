
function App() {
  var posts = [
    {name: "Ujjawal", content: "test 1"},
    {name: "Test 2", content: "Hellooooooo"},
    {name: "Ram", content: "I am ram"},
    {name: "Shyam", content: "I am shyam"},
    {name: "Ramu", content: "I am ramu"},
    {name: "Clock", content: "I am clock"},
    // {name: "Clock", content: "I am clock"},

  ]

  setInterval(()=>{
    posts.push({"name":"Raman","content":"Pushing"})
    console.log(posts)
  },1000)

  let postComponents = posts.map(p=> <Post name={p.name} content={p.content} />)

  // for(let i=0;i<posts.length;i++){
  //   postComponents.push(<Post name={posts[i].name} content={posts[i].content}/>)
  // }

  return (

    <div>
      <h1>Linkedin !!!</h1>
      {postComponents}

    </div>
    
  )
}




function Post(props:any){
  return (
    <div style={{margin:20, borderRadius:20,padding:20, fontSize:20,border:"2px solid black"}}>
    <div>
      <b>{props.name}</b>
    </div>
    <div>
      {props.content}
    </div>

    </div>
  )
}

export default App
