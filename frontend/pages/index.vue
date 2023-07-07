<template>
	<view class="pages">
		<!-- <Map :address="this.address"></Map> -->
		<Chat :class="(pageIndex==0?'':'hidden')" @pageTo="pageTo" :link="link"></Chat>
	</view>
</template>

<script>
	import Chat from './chat.vue'
	import Map from './map.vue'
	export default {
		components: {
			Chat,
			Map,
		},
		data() {
			return {
				pageIndex: 0,
				address: "武汉市洪山区卓刀泉北路39号A栋408"
			}
		},
	}
</script>

<style>
	.pages {
		position: relative;
		width: 100vw;
		height: 100vh;
		background: linear-gradient(30deg,rgba(113, 72, 248,0.03) 0%,rgba(233, 172, 253, 0.1) 50%,rgba(166, 112, 235,.12) 100%);
	}
	.page {
		position: absolute;
		width: 100%;
		height: calc(100% - 60px);
	}
	.hidden {
		display: none;
	}
    /* new change - start */
	.sider {
        width: 60px;
        position: fixed;
		display: flex;
        flex-direction: column;
		justify-content: center;
		height: 100vh;
		padding: 40px 0;
		background-color: #680e6f;
	}
    /* new change - end */
	.sider .name {
		font-size: 22px;
		font-weight: bold;
		color: #ffffff;
        text-align: center;
		white-space: nowrap;
        transform: rotate(-90deg);
	}
</style>
