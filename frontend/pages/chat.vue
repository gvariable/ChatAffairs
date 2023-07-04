<template>
	<view :class="'page page_index'+(pageIndex==0?'':' hidden')">
		<view v-if="!msgList.length" class="infoBox">
			<view class="welcome">欢迎使用 政务+</view>
			<view class="tips">HackDay白嫖零食队🍖🌭🌮🍤</view>
		</view>
		<scroll-view v-else scroll-y="true" class="msgList" :scroll-top="scrollTop" scroll-with-animation="true">
			<view class="list">
				<view v-for="item,index in msgList" class="msg">
					<view v-if="item.from==='user'" class="user">
						<text selectable="true">{{item.content}}</text>
					</view>
					<view v-else class="chatga">
						<view>
							<view class="content">
								<svg v-show="item.markup" :id="'id'+index" style="width: 55vw; height: 50vh"></svg>
								<view class="answer">
									<u-parse v-if="item.parsed" class="preview" :content="item.parsed"></u-parse>
									<text selectable="true">{{item.content}}</text>
									<view v-if="index===msgList.length-1&&running" class="blink"></view>
								</view>
							</view>
						</view>
					</view>
				</view>
			</view>
			<view class="space" style="height: 50px;"></view>
		</scroll-view>
		<view class="qstBox">
			<input type="text" class="input" :maxlength="1000" v-model="qst" :disabled="closed" @confirm="switchCase">
			<a-button :type="running?'':'primary'" size="large" class="sendOrStop"
				@click="running?stopPoll():switchCase()">
				{{running?'停止':'发送'}}
			</a-button>
			<a-button :type="recording?'':'primary'" size="large" class="sendOrStop"
				@click="recording?stopVoiceInput():startVoiceInput()">
				{{recording?'输入完毕':'语音输入'}}
			</a-button>
			<view class="newCycle" @click="newCycle">
				<view class="name">新轮提问</view>
			</view>
		</view>
	</view>
</template>

<script>
	import {
		ref
	} from 'vue'
	import Recorder from 'js-audio-recorder'
	import urlencode from "urlencode";

	const baseUrl = 'http://183.195.182.126:20248/'

	function request(url, method, data) {
		return uni.request({
			url: baseUrl + url,
			method,
			data,
		})
	}
	export default {
		props: ['link'],
		data() {
			return {
				pageIndex: 0,
				msgList: [],
				qst: '',
				scrollTop: 0,
				running: false,
				recording: false,
				closed: false,
				recorder: new Recorder({
					sampleBits: 16,
					sampleRate: 16000,
					numChannels: 1,
					compiling: true
				})
			}
		},
		mounted() {
			this.scrollIntv = setInterval(() => {
				if (this.running) {
					setTimeout(() => {
						this.scrollToBottom()
					}, 500)
				}
			}, 500)
		},
		methods: {
			startVoiceInput() {
				// this.running = true;
				this.recording = true;
				Recorder.getPermission().then(
					() => {
						console.log("开始录音");
						this.recorder.start();
					},
					(error) => {
						this.$message({
							message: "请先允许该网页使用麦克风",
							type: "info",
						});
						console.log(`${error.name} : ${error.message}`);
					}
				);
			},
			stopVoiceInput() {
				this.recording = false;
				if (this.recorder) {
					let blob = this.recorder.getPCMBlob();
					this.baiduGetSpeech2Text(blob);
				}
			},
			clearTime() {
				for (let i = 0; i < 10000; i++) {
					clearInterval(i)
					clearTimeout(i)
				}
			},
			async print(ans, time) {
				clearInterval(this.printIntv)
				time = time || 800
				let words = ans.slice(this.msgList[this.msgList.length - 1].content.length)
				this.msgList[this.msgList.length - 1].content = ans.slice(0, this.msgList[this.msgList.length - 1]
					.content.length)
				if (words.length > 0) {
					await new Promise((resolve) => {
						this.printIntv = setInterval(() => {
							if (this.msgList[this.msgList.length - 1].content.length >= ans.length) {
								clearInterval(this.printIntv)
								resolve()
							}
							this.msgList[this.msgList.length - 1].content = ans.slice(0, this.msgList[
								this.msgList.length - 1].content.length + 1)
						}, Math.floor(time / words.length))
					})
				}
			},
			newCycle() {
				this.clearTime()
				this.scrollIntv = setInterval(() => {
					if (this.running) {
						setTimeout(() => {
							this.scrollToBottom()
						}, 500)
					}
				}, 500)
				this.msgList = []
				this.modeExpStatus = 0
				this.running = false
				this.closed = false
			},
			stopPoll() {
				this.clearTime()
				this.running = false
			},
			scrollToBottom() {
				this.$nextTick(() => {
					uni.createSelectorQuery().in(this).select('.msgList .list').boundingClientRect((res) => {
						let top = res.height - 400;
						if (top > 0) {
							this.scrollTop = top;
						}
					}).exec()
				})
			},
			async switchCase() {
				if (this.running || !this.qst.trim().length) {
					return
				}
				this.msgList = [...this.msgList, {
					from: 'user',
					content: this.qst
				}, {
					from: 'chatga',
					content: ''
				}]
				this.running = true
				let qst = this.qst
				this.qst = ''
				setTimeout(() => {
					this.qst = ''
				}, 100)
				let data = {}
				data = await this.chat(qst)
				this.msgList[this.msgList.length - 1].task_id = data.task_id
			},
			baiduGetText2Speech(text) {
				const audio = new Audio();
				audio.src = "http://127.0.0.1:10001/text2speech_api?tex=" + urlencode(urlencode(text)) + "&cuid=zhengwuplus_hackday&ctp=1&lan=zh&per=106";
				audio.play();
			},
			baiduGetSpeech2Text(blob) {
				const len = blob.size;
				const reader = new FileReader();
				reader.readAsDataURL(blob);
				let voice_prepared = false
				let result = ""
				let error = false
				reader.onloadend = function() {
					const speech = reader.result.split(",")[1];
					const data = {
						"format": "pcm",
						"rate": 16000,
						"dev_pid": 80001,
						"channel": 1,
						"cuid": "zhengwuplus_hackday",
						"len": len,
						"speech": speech,
					}
					const request = uni.request({
						url: 'http://127.0.0.1:10001/voice_api',
						method: 'POST',
						data: data,
						header: {
							'Content-Type': 'application/json'
						},
						success: (res) => {

							if (res.data.err_no == 0) {
								result = res.data.result[0]
								voice_prepared = true
							} else {
								error = true
							}

						}
					})
				}
				setTimeout(() => {
					if (voice_prepared) {
						this.qst = result
						this.switchCase();
					}
				}, 2000)

			},
			async chat(qst) {
				let list = []
				this.msgList.slice(0, -1).forEach(item => {
					if (item.from == 'user') {
						list.push({
							consult: item.content,
							lawyer: ''
						})
					} else {
						list[list.length - 1].lawyer = item.content
					}
					return {
						content: item.content,
						role: item.from == 'user' ? 'user' : 'assistant'
					}
				})
				let data = await this.chat_with_api(list, ans => {
					this.print(ans)
				})
				this.running = false
			},
			async chat_with_api(chat, cb) {
				let date = Math.floor(new Date().getTime() / 1000)
				let rand = parseInt(Math.random() * 100000000) + ''
				for (let i = rand.length; i < 8; i++) {
					rand = '0' + rand
				}
				let query_id = date + '-' + rand
				let ans = await new Promise((resolve) => {
					let intv = setInterval(async () => {
						let res = await request('chat_stream_pro', 'POST', {
							query_id,
							chat
						})
						let status = res.data.status
						let answer = res.data.response
						cb && cb(answer)
						if (status == 1) {
							clearInterval(intv)
							resolve(answer)
							this.baiduGetText2Speech(answer);
						}
					}, 1000)
				})
				return ans
			}
		}
	}
</script>

<style>
	/* mask */
	.mask {
		position: fixed;
		top: 0;
		left: 0;
		display: flex;
		justify-content: center;
		align-items: center;
		width: 100vw;
		height: 100vh;
		background-color: rgba(0, 0, 0, .1);
		mask: true;
		z-index: 1;
	}

	.mask .box {
		position: relative;
		width: 80%;
		max-width: 600px;
		height: calc(100% - 80px);
		color: #111;
		background-color: #fff;
		border-radius: 5px;
		overflow: hidden;
		box-shadow: 0 0 10px 0 rgba(0, 0, 0, .1);
	}

	.mask .box .close {
		position: absolute;
		top: 15px;
		right: 15px;
		font-size: 18px;
		cursor: pointer;
	}

	.mask .box .close:hover {
		color: #567bf7;
	}

	.mask .box .preview {
		height: calc(100% - 50px);
		padding: 20px 30px;
		overflow-y: scroll;
	}

	.mask .box .btns {
		display: flex;
		align-items: center;
		height: 50px;
		padding: 0 20px;
		background-color: #ecf0fd;
	}

	/*  */
	.page_index .infoBox {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		padding-bottom: 120px;
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		overflow: hidden;
	}

	.page_index .infoBox .welcome {
		margin-bottom: 10px;
		font-size: 48px;
		font-weight: bold;
		color: #800080;
	}

	.page_index .infoBox .tips {
		margin-bottom: 50px;
		font-size: 18px;
		text-align: center;
	}

	.page_index .infoBox .card {
		display: flex;
		padding: 30px 15px 35px;
		background-color: rgba(201, 147, 255, 0.1);
		border-radius: 8px;
	}

	.page_index .infoBox .card .split {
		width: 1px;
		height: 80px;
		margin-top: 50px;
		background-color: #800080;
	}

	.page_index .infoBox .card .block {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 0 30px;
	}

	.page_index .infoBox .card .block .title {
		position: relative;
		margin-bottom: 30px;
		font-size: 18px;
		font-weight: bold;
	}

	.page_index .infoBox .card .block .title::after {
		position: absolute;
		left: -5px;
		bottom: -3px;
		width: calc(100% + 10px);
		height: 4px;
		content: '';
		background: linear-gradient(90deg, rgba(128, 0, 128, 1.0) 0%, rgba(86, 123, 247, 0) 100%);
	}

	/* msgList */
	.page_index .msgList {
		position: absolute;
		left: 0;
		top: 0;
		width: 100%;
		height: calc(100% - 100px);
		padding: 20px 8% 0px;
		overflow-y: scroll;
		white-space: pre-wrap;
		word-break: break-all;
	}

	.page_index .msgList .closed {
		display: flex;
		justify-content: center;
		align-items: center;
	}

	.page_index .msgList .closed .split {
		flex: 1;
		height: 1px;
		margin: 0 10px;
		background-color: #9ec1f5;
	}

	.page_index .msgList .msg {
		margin-bottom: 20px;
	}

	.page_index .msgList .msg .user {
		width: fit-content;
		max-width: 70%;
		margin-left: auto;
		padding: 10px 15px;
		color: #fff;
		background-color: #a642b0;
		border-radius: 10px;
	}

	.page_index .msgList .msg .chatga {
		width: fit-content;
		min-width: 30%;
		max-width: 70%;
		margin-right: auto;
	}

	.page_index .msgList .msg .chatga .status {
		display: flex;
		margin-bottom: 10px;
	}

	.page_index .msgList .msg .chatga .status .label {
		white-space: nowrap;
	}

	.page_index .msgList .msg .chatga .status .value {
		display: flex;
		align-items: center;
		margin-left: 10px;
		font-weight: bold;
	}

	.page_index .msgList .msg .chatga .content {
		padding: 15px 15px;
		color: #111;
		background-color: #fff;
		border: 1px solid #8756a6;
		border-radius: 10px;
	}

	.page_index .msgList .msg .chatga .content .flow {
		width: 100%;
		margin-bottom: 10px;
	}

	.page_index .msgList .msg .chatga .content .answer {
		white-space: pre-wrap;
	}

	.page_index .msgList .msg .chatga .content .answer .blink {
		display: inline-block;
		position: relative;
		top: 3px;
		width: 5px;
		height: 16px;
		margin-left: 3px;
		background-color: #444;
		animation: blink 0.6s infinite;
	}

	@keyframes blink {
		0% {
			opacity: 1;
		}

		30% {
			opacity: 0;
		}

		70% {
			opacity: 0;
		}

		100% {
			opacity: 1;
		}
	}

	.page_index .msgList .msg .chatga .content .cases.fold {
		height: 0;
		margin: 0;
		padding: 0;
		border: 0px;
	}

	.page_index .msgList .msg .chatga .content .cases .list {
		flex: 1;
		display: flex;
		flex-wrap: wrap;
		font-size: 14px;
	}

	.page_index .qstBox {
		position: fixed;
		left: 8%;
		bottom: 20px;
		display: flex;
		align-items: flex-end;
		width: 84%;
	}

	.page_index .qstBox .newCycle {
		display: flex;
		justify-content: center;
		align-items: center;
		width: 120px;
		height: 50px;
		border-radius: 5px;
		color: #6f0071;
		background: linear-gradient(30deg, rgba(171, 19, 249, 0.0) 0%, rgba(255, 178, 240, 0.1) 50%, rgba(246, 77, 214, 0.2) 100%);
		background-color: #fff;
		border: 1px solid #8b2193;
		border-radius: 5px;
		cursor: pointer;
		overflow: hidden;
	}

	.page_index .qstBox .newCycle:hover {
		filter: brightness(1.05);
	}

	.page_index .qstBox .newCycle .icon {
		width: 20px;
		height: 20px;
		margin-right: 5px;
	}

	.page_index .qstBox .input {
		flex: 1;
		min-height: 50px !important;
		margin: 0 20px;
		padding: 12px 20px;
		font-size: 16px;
		background-color: #fff;
		border: 1px solid #800080;
		border-radius: 5px;
		box-shadow: 0 0 10px 0 rgba(168, 199, 245, 0.2);
	}

	.page_index .qstBox .sendOrStop {
		box-sizing: border-box;
		height: 50px;
		padding: 0 20px;
		border: 1px solid #ffffff;
		margin-right: 20px;
	}

	.page_index .qstBox .sendOrStop.ant-btn-primary {
		background-color: #800080;
	}

	@media screen and (max-width: 500px) {
		.page_index .infoBox {
			/* display: none; */
		}

		.page_index .infoBox .welcome {
			font-size: 27px;
			margin-bottom: 20px;
		}

		.page_index .infoBox .tips {
			margin-bottom: 10px;
		}

		.page_index .infoBox .card {
			display: none;
		}

		.page_index .infoBox .tips2 {
			display: none;
		}

		.page_index .infoBox .modeBox {
			position: absolute;
			bottom: 120px;
		}

		.page_index .qstBox {
			left: 5%;
			bottom: 20px;
			width: 90%;
		}

		.page_index .qstBox .newCycle {
			height: 40px;
		}

		.page_index .qstBox .input {
			margin: 0 10px;
			padding: 6px 10px;
			min-height: 40px !important;
		}

		.page_index .qstBox .sendOrStop {
			height: 40px;
			padding: 0 10px;
		}

		.page_index .qstBox .newCycle {
			width: 40px;
		}

		.page_index .qstBox .newCycle .icon {
			margin-right: 0;
		}

		.page_index .qstBox .newCycle .name {
			display: none;
		}

		.page_index .msgList {
			height: calc(100% - 70px);
			padding: 15px 5% 0;
		}

		.page_index .msgList .msg .chatga {
			max-width: 100%;
		}
	}
</style>