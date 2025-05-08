all:
	echo "Hello, World!"

baseline-setup-w14:
	helm install oai-cu ./charts/oai-5g-ran-baseline/oai-cu
	helm install oai-du ./charts/oai-5g-ran-baseline/oai-du-fhi72

baseline-update-w18:
	helm upgrade oai-du ./charts/oai-5g-ran-baseline/oai-du-fhi72 -f ./charts/oai-5g-ran-baseline/oai-du-fhi72/values-2025.w18.yaml

baseline-update-w14:
	helm upgrade oai-du ./charts/oai-5g-ran-baseline/oai-du-fhi72 -f ./charts/oai-5g-ran-baseline/oai-du-fhi72/values.yaml

swapran-setup-w14:
	helm install oai-cu ./charts/oai-5g-ran-swapran/oai-cu
	helm install oai-du ./charts/oai-5g-ran-swapran/oai-du-fhi72

swapran-update-w18:
	helm upgrade oai-du ./charts/oai-5g-ran-swapran/oai-du-fhi72 -f ./charts/oai-5g-ran-swapran/oai-du-fhi72/values-2025.w18.yaml

swapran-update-w14:
	helm upgrade oai-du ./charts/oai-5g-ran-swapran/oai-du-fhi72 -f ./charts/oai-5g-ran-swapran/oai-du-fhi72/values.yaml

cleanup:
	helm uninstall oai-cu --ignore-not-found
	helm uninstall oai-du --ignore-not-found