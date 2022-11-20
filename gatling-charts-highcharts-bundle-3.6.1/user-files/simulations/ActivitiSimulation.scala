/***
* @author lujianbin
*
*/
// package activiti

import scala.concurrent.duration._
import io.gatling.core.structure.PopulationBuilder
import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.io.Source

class ActivitiSimulation extends Simulation {

  val kcUrl = default("kcUrl", "http://identity-activiti7.172.16.33.51.nip.io")
  val realm = default("kcRealm", "activiti")

  val appUrl = default("appUrl", "http://gateway-activiti7.172.16.33.51.nip.io")

  val httpProtocol = http
    // Here is the root for all relative URLs
    .baseUrl(appUrl)
    .acceptHeader("text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
    .doNotTrackHeader("1")
    .acceptLanguageHeader("en-US,en;q=0.5")
    .acceptEncodingHeader("gzip, deflate")
    .userAgentHeader("Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:16.0) Gecko/20100101 Firefox/16.0")

  var global_token = ""
    
  object Auth {
      val authHrUser = exec(http("authHrUser")
                              .post(s"$kcUrl/auth/realms/$realm/protocol/openid-connect/token")
                              .formParam("client_id", "activiti")
                              .formParam("grant_type", "password")
                              .formParam("username", "hruser")
                              .formParam("password", "password")
                              .check(status.is(200))
                              .check(jsonPath("$.access_token")
                               .saveAs("token"))
      )
      .exec{ session =>
                          println("session:"+session)
                          println("access_token :" + session("token").as[String])
                          global_token = session("token").as[String]
                          println(global_token)
                          session
                        }
  }

  object App {
      val getProcessDefinitionsList = exec(
        http("getProcessDefinitions")
          .get("/rb/v1/process-definitions")
          .header("Authorization", "Bearerer ${token}")
      )

      // val feeder = csv("activitiProcessDefinition.csv")
      val startProcess = exec(
        session => session.set("my_token", global_token)
      )
      .exec(
        http("startProcess")
          .post("/rb/v1/process-instances")
          .headers(
            Map(
              // "Content-Type" -> "application/json",
              "Authorization"->("Bearer "+ "${my_token}")
              )
            )
          .body(RawFileBody("raw-body.json")).asJson
          .check(status.is(200))
          .check(jsonPath("$..id")
           .saveAs("instance_id"))
      )

      val getProcessInstanceTask = exec(
        session => session.set("my_token", global_token)
      )
      .exec(
        http("getProcessInstanceTask")
          .get("/rb/v1/process-instances/${instance_id}/tasks")
          .headers(
            Map(
              // "Content-Type" -> "application/json",
              "Authorization"->("Bearer "+ "${my_token}")
              )
            )
          .check(status.is(200))
          .check(jsonPath("$._embedded.tasks[*].id").findAll.saveAs("taskIds"))
      )

      val claimTasks = exec(
        session => session.set("my_token", global_token)
      )
      .exec(
        foreach("${taskIds}", "taskId") {
            exec(http("claimTask")
              .post("/rb/v1/tasks/${taskId}/claim?assignee=hruser")
              .headers(
                Map(
                  // "Content-Type" -> "application/json",
                  "Authorization"->("Bearer "+ "${my_token}")
                )
              )
              .check(status.is(200))
            )
          }
      )

      val completeTasks = exec(
        session => session.set("my_token", global_token)
      )
      .exec(
          foreach("${taskIds}", "taskId") {
          //   exec(http("claimTask")
          //     .post("/rb/v1/tasks/${taskId}/claim?assignee=hruser")
          //     .headers(
          //       Map(
          //         // "Content-Type" -> "application/json",
          //         "Authorization"->("Bearer "+ global_token)
          //       )
          //     )
          //     .check(status.is(200))
          //   )
            exec(http("completeTask")
              .post("/rb/v1/tasks/${taskId}/complete")
              .headers(
                Map(
                  // "Content-Type" -> "application/json",
                  "Authorization"->("Bearer "+ "${my_token}")

                  )
              )
              .check(status.is(200))
            )
          }
      )

      val getUserTasks = exec(
        http("getUserTasks")
        .get("/rb/v1/tasks?page=0&size=100")
        .headers(
          Map(
            "Authorization"->("Bearer "+ global_token)
          )
        )
        .check(status.is(200))
        .check(jsonPath("$._embedded.tasks[*].id").findAll.saveAs("taskIds"))
      )

      val getUserTasks1 = exec(
        http("getUserTasks1")
        .get("/rb/v1/tasks?page=2&size=100")
        .headers(
          Map(
            "Authorization"->("Bearer "+ global_token)
          )
        )
        .check(status.is(200))
        .check(jsonPath("$._embedded.tasks[*].id").findAll.saveAs("taskIds"))
      )
  }

  // A scenario is a chain of requests and pauses
  val get_token =  scenario("GetToken").exec(Auth.authHrUser).pause(2)
  val get_process_definition = scenario("GetProcessDefinition").exec(App.getProcessDefinitionsList).pause(2)
  val start_process = scenario("Execute A Simple Process")
    .exec(Auth.authHrUser)
    .exec(App.startProcess)
    .exec(App.getProcessInstanceTask)
    .exec(App.claimTasks)
    .exec(App.completeTasks)

  setUp(
    // get_token.inject(atOnceUsers(1)),
    // start_process.inject(atOnceUsers(1))
    start_process.inject(atOnceUsers(1))

  )
  .protocols(httpProtocol)



  def default[T](option: String, defaultValue: T): T = {
    if (System.getProperty(option) == null)
      return defaultValue 

    (defaultValue match {
      case t: String => System.getProperty(option)
      case t: Int => System.getProperty(option).toInt
      case t@_ => throw new IllegalArgumentException("unsupported type")
    }).asInstanceOf[T]
  }

}

