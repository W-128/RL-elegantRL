/*
 * Copyright 2011-2021 GatlingCorp (https://gatling.io)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


import scala.concurrent.duration._
import io.gatling.core.structure.PopulationBuilder
import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.io.Source

class request_test_edf extends Simulation {

  val serverHost = " http://localhost:5000"
  val httpProtocol = http
    // Here is the root for all relative URLs
    .baseUrl(serverHost)
    // Here are the common headers
    .acceptHeader("text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
    .doNotTrackHeader("1")
    .acceptLanguageHeader("en-US,en;q=0.5")
    .acceptEncodingHeader("gzip, deflate")
    .userAgentHeader("Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:16.0) Gecko/20100101 Firefox/16.0")
  
  val feeder = csv("rtl_and_request_id.csv")
 
  object CompleteTask {
      val complete = 
        feed(feeder)
        .exec(
          http("complete-task-request_id=${request_id}rtl=${rtl}")
          .get("/complete_task_edf/${request_id}/${rtl}")
          .check(status.is(200))
        )

  }

  var steps = Seq[Int]()
  var a = 0
  // var itr = 0
  // val bufferedSource = Source.fromFile("count.csv")
  for (line <- Source.fromFile("..//user-files//simulations//traffic.csv", "UTF-8").getLines) {
    steps = steps :+ line.toInt
  }
  // bufferedSource.close
  // steps = steps ++ steps
  println(steps)

  val injectionProfile = steps.flatMap(
    load => Seq(
      heavisideUsers(load) during(1 seconds)
    )
  )


  val start_process = scenario("Execute A Simple Process")
    .exec(CompleteTask.complete)

  setUp(
    start_process.inject(
      injectionProfile
    )
  )
  .protocols(httpProtocol)
}
