<script lang="ts">
	import { getContext, createEventDispatcher } from 'svelte';
	import Modal from '../common/Modal.svelte';

    const i18n = getContext('i18n');
    const dispatch = createEventDispatcher();

	export let show = false;
    export let title = 'Delete?';
</script>

<Modal bind:show size="sm">
    <div class=" flex justify-between dark:text-gray-300 px-5 pt-4 pb-0.5">
        <div class=" text-lg font-medium self-center">{$i18n.t(`${title}`)}</div>
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

    <div class="px-5 pt-4 pb-5 w-full">
        <div class="flex justify-end">
            <div class="flex  items-end space-x-1 mt-1.5">
                <div class="flex justify-end gap-1">
                    <button
                        class=" self-center flex items-center gap-1 px-3.5 py-2 rounded-xl text-sm font-medium bg-neutral-300 hover:bg-neutral-200 text-white"
                        on:click={() => {
                            show = false;
                        }}
                    >
                        {$i18n.t('Cancel')}
                    </button>
                    <button
                        class=" self-center flex items-center gap-1 px-3.5 py-2 rounded-xl text-sm font-medium bg-red-400 hover:bg-red-300 text-white"
                        on:click={() => {
                            dispatch('confirm');
                            show = false;
                        }}
                    >
                        {$i18n.t('Delete')}
                    </button>
                </div>
            </div>
        </div>
    </div>
</Modal>
