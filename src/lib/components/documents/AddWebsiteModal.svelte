<script lang="ts">
	import { onMount, getContext } from 'svelte';

	import { getDocs } from '$lib/apis/documents';
	import Modal from '../common/Modal.svelte';
	import { documents } from '$lib/stores';
	import Tags from '../common/Tags.svelte';

	const i18n = getContext('i18n');

	export let show = false;
	export let uploadWebsite: Function;
	let website = '';
	let tags = [];

	const submitHandler = async () => {
		uploadWebsite(website)
		website = '';
		show = false;
	};

	const addTagHandler = async (tagName) => {
		if (!tags.find((tag) => tag.name === tagName) && tagName !== '') {
			tags = [...tags, { name: tagName }];
		} else {
			console.log('tag already exists');
		}
	};

	const deleteTagHandler = async (tagName) => {
		tags = tags.filter((tag) => tag.name !== tagName);
	};

	onMount(() => {});
</script>

<Modal size="sm" bind:show>
	<div>
		<div class=" flex justify-between dark:text-gray-300 px-5 pt-4">
			<div class=" text-lg font-medium self-center">{$i18n.t('Add Website')}</div>
			<button
				class="self-center"
				on:click={() => {
					show = false;
				}}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 20 20"
					fill="currentColor"
					class="w-5 h-5"
				>
					<path
						d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z"
					/>
				</svg>
			</button>
		</div>
		<div class="flex flex-col md:flex-row w-full px-5 py-4 md:space-x-4 dark:text-gray-200">
			<div class=" flex flex-col w-full sm:flex-row sm:justify-center sm:space-x-6">
				<form
					class="flex flex-col w-full"
					on:submit|preventDefault={() => {
						submitHandler();
					}}
				>
					<div class="mb-3 w-full">
						<input
							class="w-full text-sm font-medium py-3 bg-gray-100 hover:bg-gray-200 dark:bg-gray-850 dark:hover:bg-gray-800 rounded-xl py-3 px-1 scrollbar-hidden outline-none resize-none dark:text-gray-100"
							bind:value={website}
							id="upload-website-input"
							type="text"
							placeholder="Enter website URL"
						/>
					</div>

					<div class=" flex flex-col space-y-1.5">
						<div class="flex flex-col w-full">
							<div class=" mb-1.5 text-xs text-gray-500">{$i18n.t('Tags')}</div>

							<Tags {tags} addTag={addTagHandler} deleteTag={deleteTagHandler} />
						</div>
					</div>

					<div class="flex justify-end pt-5 text-sm font-medium">
						<button
							class=" px-4 py-2 bg-emerald-700 hover:bg-emerald-800 text-gray-100 transition rounded-lg"
							type="submit"
						>
							{$i18n.t('Save')}
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
</Modal>

<style>
	input::-webkit-outer-spin-button,
	input::-webkit-inner-spin-button {
		/* display: none; <- Crashes Chrome on hover */
		-webkit-appearance: none;
		margin: 0; /* <-- Apparently some margin are still there even though it's hidden */
	}

	.tabs::-webkit-scrollbar {
		display: none; /* for Chrome, Safari and Opera */
	}

	.tabs {
		-ms-overflow-style: none; /* IE and Edge */
		scrollbar-width: none; /* Firefox */
	}

	input[type='number'] {
		-moz-appearance: textfield; /* Firefox */
	}
</style>
