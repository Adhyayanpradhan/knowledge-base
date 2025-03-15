from locust import HttpUser, task, between
from scenarios import BasicScenario

class LoadBalancerUser(HttpUser):
    wait_time = between(1, 5)  # Wait time between tasks

    @task
    def basic_scenario(self):
        scenario = BasicScenario(self.client)
        scenario.run()