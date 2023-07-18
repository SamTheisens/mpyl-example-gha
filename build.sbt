name                     := "sbt-multi-project-example"
ThisBuild / organization := "organization"

lazy val mpyl = project
  .in(file("."))
  .aggregate(sbtservice)

lazy val sbtservice = (project in file("projects/sbt-service")).settings(name := "sbtservice")
lazy val sparkJob =
  (project in file("projects/spark-job")).settings(name := "sparkJob")
