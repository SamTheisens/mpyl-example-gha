package nl.vandebron.api.mpyl

//Trigger a change

object Main extends cask.MainRoutes {
  @cask.get("/")
  def hello() = {
    println("Received request")
    "Hello World!"
  }

  initialize()
}
