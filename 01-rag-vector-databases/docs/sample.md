# Kubernetes Network Policies

Network Policies in Kubernetes allow you to control traffic flow at the IP address or port level.
This is useful for implementing microsegmentation and zero-trust networking.

Cilium is a popular CNI that provides more advanced network policies using eBPF technology.
It offers better performance and more powerful security features compared to standard Kubernetes NetworkPolicies.

Platform engineers should understand both native NetworkPolicies and Cilium policies.
