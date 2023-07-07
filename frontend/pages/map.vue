<template>
	<view id="gaode-map" style="width: 100%; height: 100%">
	</view>
</template>

<script>
	import AMapLoader from '@amap/amap-jsapi-loader';
	window._AMapSecurityConfig = {
		// 设置安全密钥
		securityJsCode: 'c83702194c90195f6b2717e2297ba98b',
	}
	export default {
		props: {
			address: { // Define the address prop
				type: String,
				required: true
			}
		},
		data() {
			return {
				map: null
			}
		},
		methods: {
			initAMap() {
				AMapLoader.load({
					"key": "14a19066b40a559c31740cdfe3ed2be6",
					"version": "2.0",
					"plugins": ["AMap.AutoComplete", "AMap.Geocoder"],
				}).then((AMap) => {
					this.map = new AMap.Map('gaode-map', {
						viewMode: "2D", //  是否为3D地图模式
						zoom: 13, // 初始化地图级别
						center: [114.413481, 30.507734], //中心点坐标  郑州
						resizeEnable: true
					});


					let geocoder = new AMap.Geocoder();

					geocoder.getLocation(this.address, (status, result) => {
						if (status === 'complete' && result.info === 'OK') {
							let lnglat = [result.geocodes[0].location.getLng(), result.geocodes[0].location
								.getLat()
							];
							this.map.setZoomAndCenter(15, lnglat);
							const marker = new AMap.Marker({
							    position: lnglat,
							    title: '目标地点'
							})
							  
							this.map.add(marker)
						}
					})
				}).catch(e => {
					console.log(e);
				});
			}
		},
		mounted() {
			//DOM初始化完成进行地图初始化
			this.initAMap()
		}
	}
</script>

<style>
</style>