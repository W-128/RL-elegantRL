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

class request_test extends Simulation {

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
          .get("/complete_task/${request_id}/${rtl}")
          .check(status.is(200))
        )

  }
  val source = Source.fromFile("..//user-files//simulations//concurrent_request_num.csv", "UTF-8")
  val concurrent_num_per_second = source.getLines().toArray
  source.close()

  def scnList()={
    var scnList = new Array[PopulationBuilder](concurrent_num_per_second.length)
    var i = 0
    while(i<concurrent_num_per_second.length) {
      var scen = scenario("Get CompleteTask"+i+"th second")
        .pause(i)
        .exec(CompleteTask.complete)
        .inject(atOnceUsers(concurrent_num_per_second(i).toInt))
      scnList(i) = scen
      i = i + 1
    }
    scnList
  }

   setUp(scnList: _*).protocols(httpProtocol)
}
