all:
	echo "Hello, World!"

baseline-setup-w29:
	helm install oai-cu ./charts/oai-5g-ran-baseline/oai-cu
	helm install oai-du ./charts/oai-5g-ran-baseline/oai-du-fhi72

baseline-update-w29:
	helm upgrade oai-du ./charts/oai-5g-ran-baseline/oai-du-fhi72 -f ./charts/oai-5g-ran-baseline/oai-du-fhi72/values.yaml

baseline-update-w30:
	helm upgrade oai-du ./charts/oai-5g-ran-baseline/oai-du-fhi72 -f ./charts/oai-5g-ran-baseline/oai-du-fhi72/values-2025.w30.yaml

baseline-update-w31:
	helm upgrade oai-du ./charts/oai-5g-ran-baseline/oai-du-fhi72 -f ./charts/oai-5g-ran-baseline/oai-du-fhi72/values-2025.w31.yaml

swapran-setup-w29:
	helm install oai-cu ./charts/oai-5g-ran-swapran/oai-cu
	helm install oai-du ./charts/oai-5g-ran-swapran/oai-du-fhi72

swapran-update-w29:
	helm upgrade oai-du ./charts/oai-5g-ran-swapran/oai-du-fhi72 -f ./charts/oai-5g-ran-swapran/oai-du-fhi72/values.yaml

swapran-update-w30:
	helm upgrade oai-du ./charts/oai-5g-ran-swapran/oai-du-fhi72 -f ./charts/oai-5g-ran-swapran/oai-du-fhi72/values-2025.w30.yaml

swapran-update-w31:
	helm upgrade oai-du ./charts/oai-5g-ran-swapran/oai-du-fhi72 -f ./charts/oai-5g-ran-swapran/oai-du-fhi72/values-2025.w31.yaml

cleanup:
	helm uninstall oai-cu --ignore-not-found
	helm uninstall oai-du --ignore-not-found