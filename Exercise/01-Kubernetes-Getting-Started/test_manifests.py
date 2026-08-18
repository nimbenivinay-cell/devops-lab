import unittest
import yaml
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class KubernetesGettingStartedTestCase(unittest.TestCase):
    def test_pod_manifest(self):
        pod_file = os.path.join(BASE_DIR, "pod.yaml")
        self.assertTrue(os.path.exists(pod_file), "pod.yaml does not exist")
        with open(pod_file, "r", encoding="utf-8") as f:
            pod = yaml.safe_load(f)
        self.assertEqual(pod.get("apiVersion"), "v1")
        self.assertEqual(pod.get("kind"), "Pod")
        self.assertEqual(pod.get("metadata", {}).get("name"), "hello-k8s")
        labels = pod.get("metadata", {}).get("labels", {})
        self.assertEqual(labels.get("app"), "hello-k8s")
        containers = pod.get("spec", {}).get("containers", [])
        self.assertEqual(len(containers), 1)
        self.assertEqual(containers[0].get("name"), "hello-k8s")
        self.assertIn("nginx", containers[0].get("image"))
        ports = containers[0].get("ports", [])
        self.assertEqual(ports[0].get("containerPort"), 80)
        self.assertIn("resources", containers[0])

    def test_service_manifest(self):
        svc_file = os.path.join(BASE_DIR, "service.yaml")
        self.assertTrue(os.path.exists(svc_file), "service.yaml does not exist")
        with open(svc_file, "r", encoding="utf-8") as f:
            svc = yaml.safe_load(f)
        self.assertEqual(svc.get("apiVersion"), "v1")
        self.assertEqual(svc.get("kind"), "Service")
        self.assertEqual(svc.get("metadata", {}).get("name"), "hello-k8s")
        spec = svc.get("spec", {})
        self.assertEqual(spec.get("type"), "NodePort")
        self.assertEqual(spec.get("selector", {}).get("app"), "hello-k8s")
        ports = spec.get("ports", [])
        self.assertEqual(len(ports), 1)
        self.assertEqual(ports[0].get("port"), 80)
        self.assertEqual(ports[0].get("targetPort"), 80)

    def test_deployment_manifest(self):
        deploy_file = os.path.join(BASE_DIR, "deployment.yaml")
        self.assertTrue(os.path.exists(deploy_file), "deployment.yaml does not exist")
        with open(deploy_file, "r", encoding="utf-8") as f:
            deploy = yaml.safe_load(f)
        self.assertEqual(deploy.get("apiVersion"), "apps/v1")
        self.assertEqual(deploy.get("kind"), "Deployment")
        self.assertEqual(deploy.get("metadata", {}).get("name"), "hello-k8s-deployment")
        spec = deploy.get("spec", {})
        self.assertGreaterEqual(spec.get("replicas", 0), 1)
        self.assertEqual(spec.get("selector", {}).get("matchLabels", {}).get("app"), "hello-k8s")
        template_spec = spec.get("template", {}).get("spec", {})
        containers = template_spec.get("containers", [])
        self.assertEqual(len(containers), 1)
        self.assertIn("nginx", containers[0].get("image"))

if __name__ == "__main__":
    unittest.main()
