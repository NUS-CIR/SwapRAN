all:
	echo "Hello, World!"

bootstrap:
	helm install oai-5g-basic ./charts/oai-5g-core/oai-5g-basic
	helm install iperf3 oci://registry-1.docker.io/gradiantcharts/iperf3 --version 0.1.3

baseline-setup-w29:
	helm install oai-cu ./charts/oai-5g-ran-baseline/oai-cu
	helm install oai-du ./charts/oai-5g-ran-baseline/oai-du-fhi72

baseline-update-w29:
	helm upgrade oai-cu ./charts/oai-5g-ran-baseline/oai-cu -f ./charts/oai-5g-ran-baseline/oai-cu/values-2025.w29.yaml

baseline-update-w30:
	helm upgrade oai-cu ./charts/oai-5g-ran-baseline/oai-cu -f ./charts/oai-5g-ran-baseline/oai-cu/values-2025.w30.yaml

swapran-setup-w29:
	helm install f1ap-proxy ./charts/oai-5g-ran-swapran/f1ap-proxy
	helm install oai-cu ./charts/oai-5g-ran-swapran/oai-cu
	helm install oai-du ./charts/oai-5g-ran-swapran/oai-du-fhi72

# swapran-update-w41:
# 	helm upgrade oai-cu ./charts/oai-5g-ran-swapran/oai-cu -f ./charts/oai-5g-ran-swapran/oai-cu/values-2024.w41.yaml

# swapran-update-w42:
# 	helm upgrade oai-cu ./charts/oai-5g-ran-swapran/oai-cu -f ./charts/oai-5g-ran-swapran/oai-cu/values-2024.w42.yaml

# swapran-update-w43:
# 	helm upgrade oai-cu ./charts/oai-5g-ran-swapran/oai-cu -f ./charts/oai-5g-ran-swapran/oai-cu/values-2024.w43.yaml

remove_ran:
	helm uninstall f1ap-proxy --ignore-not-found
	helm uninstall oai-cu --ignore-not-found
	helm uninstall oai-du --ignore-not-found
	
cleanup:
	helm uninstall oai-5g-basic --ignore-not-found
	helm uninstall iperf3 --ignore-not-found
	helm uninstall oai-cu --ignore-not-found
	helm uninstall oai-du --ignore-not-found
	helm uninstall f1ap-proxy --ignore-not-found