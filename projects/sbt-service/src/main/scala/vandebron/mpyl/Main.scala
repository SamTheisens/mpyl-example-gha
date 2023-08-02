package nl.vandebron.api.mpyl

object Main extends cask.MainRoutes {
  println("Starting sbt service")

  @cask.get("/")
  def hello() = {
    println("Received request")
    "Hello World!"
  }

  initialize()
}
