<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { config, documents, user } from '$lib/stores';
	import { toast } from 'svelte-sonner';
    import { getKnowledgeBases, addKnowledgeBase, deleteKnowledgeBase } from '$lib/apis/configs';
	import ConfirmDeleteModal from '../../../../lib/components/admin/ConfirmDeleteModal.svelte';
	import { goto } from '$app/navigation';
    import Modal from '$lib/components/common/Modal.svelte';
	import { deleteDocByName, getDocs } from '$lib/apis/documents';

    const i18n = getContext('i18n');

    let showAddModal = false;
    let showConfirmDeleteModal = false;
    let deleteId = '';
    let newKbTitle = '';
    let knowledgeBases = [];

    let query = '';

    $: filteredKbs = knowledgeBases.filter(kb => {
        return (query === '' || kb.title.toLowerCase().includes(query.toLowerCase()));
    })

    async function fetchKnowledgeBases() {
        const res = await getKnowledgeBases(localStorage.token).catch((e) => {
            console.error(e);
            toast.error($i18n.t('Failed to fetch knowledge bases'));
        });

        if (res) {
            knowledgeBases = res;
        }
    }

    $: if(!showAddModal) {
        newKbTitle = '';
    }

    async function deleteKbById(KbId: string) {
        const kb = knowledgeBases.find((_kb) => _kb.id === KbId);

        if (!kb){
            toast.error($i18n.t('Knowledge base not found'));
            return;
        }

        const deleteDocRes = await Promise.all(
                kb.documents.map(async (doc) => {
                    return await deleteDocByName(localStorage.token, doc.name);
                })
            )

        if (deleteDocRes){
            await documents.set(await getDocs(localStorage.token));
        }

        const res = await deleteKnowledgeBase(localStorage.token, KbId).catch((e) => {
            console.error(e);
            toast.error($i18n.t('Failed to delete knowledge base'));
        });

        if (res) {
            toast.success($i18n.t('Knowledge base deleted successfully'));
            await fetchKnowledgeBases();
        }
    }

    const handleAddKnowledgeBase = async (title: string) => {
        const kb = {
            title,
            description: "",
            documents: [],
            embedding_model: "",
            type: "general"
        }

        const res = await addKnowledgeBase(localStorage.token, kb).catch((e) => {
                console.error(e);
                toast.error($i18n.t('Failed to add knowledge base'));
        });

        if (res.kb_id) {
            toast.success($i18n.t('New knowledge base added successfully'));
            goto('/admin/knowledge-bases/' + res.kb_id); 
            await fetchKnowledgeBases();
        }
    }

	onMount(async () => {
        await fetchKnowledgeBases();
	});
</script>

<Modal bind:show={showAddModal} size="sm">
    <div class=" flex justify-between dark:text-gray-300 px-5 pt-4 pb-0.5">
        <div class=" text-lg font-medium self-center">{$i18n.t('Add Knowledge Base')}</div>
        <button
            class="self-center"
            on:click={() => {
                showAddModal = false;
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
    <div class=" flex justify-between dark:text-gray-300 px-5 pt-4 pb-0.5">
        <div class="w-full flex-row">
            <div class=" self-center text-xs font-medium min-w-fit mb-1">
                {$i18n.t('Title')}
            </div>
            <input
                id="new-knowledge-base-title-input"
                aria-label={$i18n.t('Enter knowledge base title')}
                class="w-full rounded-lg py-2 px-4 text-sm border dark:border-gray-600
                dark:bg-gray-900 bg-gray-50 outline-none"
                placeholder={$i18n.t('Enter knowledge base title')}
                bind:value={newKbTitle}
            />
        </div>
    </div>

    <div class="px-5 pt-4 pb-5 w-full">
        <div class="flex justify-end">
            <div class="flex  items-end space-x-1 mt-1.5">
                <div class="flex justify-end gap-1">
                    <button
                        class=" self-center flex items-center gap-1 px-3.5 py-2 rounded-xl text-sm font-medium bg-neutral-300 hover:bg-neutral-200 text-white"
                        on:click={() => {
                            showAddModal = false;
                        }}
                    >
                        {$i18n.t('Cancel')}
                    </button>
                    <button
                        class=" self-center flex items-center gap-1 px-3.5 py-2 rounded-xl text-sm font-medium bg-green-400 hover:bg-green-300 text-white"
                        on:click={() => {
                            handleAddKnowledgeBase(newKbTitle);
                            showAddModal = false;
                        }}
                    >
                        {$i18n.t('Add')}
                    </button>
                </div>
            </div>
        </div>
    </div>
</Modal>

<ConfirmDeleteModal bind:show={showConfirmDeleteModal} title="Delete this knowledge base?" on:confirm={() => deleteKbById(deleteId)}/>

<div
	class="flex flex-col h-full justify-between space-y-3 text-sm"
>
	<div class=" space-y-3 overflow-y-scroll scrollbar-hidden h-full">
		<div>
            
			<div class=" mb-2 text-sm font-medium">{$i18n.t('Knowledge Bases')}</div>
            <div class=" flex w-full space-x-2 px-3 py-2">
                <div class="flex flex-1">
                    <div class=" self-center ml-1 mr-3">
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                            class="w-4 h-4"
                        >
                            <path
                                fill-rule="evenodd"
                                d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z"
                                clip-rule="evenodd"
                            />
                        </svg>
                    </div>
                    <input
                        class=" w-full text-sm pr-4 py-1 rounded-r-xl outline-none bg-transparent"
                        bind:value={query}
                        placeholder={$i18n.t('Search Knowledge Bases')}
                    />
                </div>
            
                <div>
                    <button
                        class=" px-2 py-2 rounded-xl border border-gray-200 dark:border-gray-600 dark:border-0 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 transition font-medium text-sm flex items-center space-x-1"
                        aria-label={$i18n.t('Add Knowledge Base')}
                        type="button"
                        on:click={() => {
                            showAddModal = true;
                            setTimeout(() => {
                                const newKbInput = document.getElementById('new-knowledge-base-title-input');
                                if (newKbInput) {
                                    newKbInput.focus();
                                }
                            }, 0);
                        }}
                    >
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 16 16"
                            fill="currentColor"
                            class="w-4 h-4"
                        >
                            <path
                                d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z"
                            />
                        </svg>
                    </button>
                </div>
            </div>
            <div class="flex flex-wrap">
                {#each filteredKbs as kb}
                    <button
                        class=" flex space-x-4 cursor-pointer text-left w-1/2 px-3 py-2 dark:hover:bg-white/5 hover:bg-black/5 rounded-xl"
                        type="button"
                        on:click={() => {
                            goto('/admin/knowledge-bases/' + kb.id);
                        }}
                    >
                        <div class=" flex flex-1 space-x-4 cursor-pointer w-full">
                            <div class=" flex items-center space-x-3">
                                <div class="p-2.5 bg-blue-400 text-white rounded-lg">
                                    <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 24 24"
                                    fill="currentColor"
                                    class="w-6 h-6"
                                    >
                                        <path
                                            fill-rule="evenodd"
                                            d="M5.625 1.5c-1.036 0-1.875.84-1.875 1.875v17.25c0 1.035.84 1.875 1.875 1.875h12.75c1.035 0 1.875-.84 1.875-1.875V12.75A3.75 3.75 0 0 0 16.5 9h-1.875a1.875 1.875 0 0 1-1.875-1.875V5.25A3.75 3.75 0 0 0 9 1.5H5.625ZM7.5 15a.75.75 0 0 1 .75-.75h7.5a.75.75 0 0 1 0 1.5h-7.5A.75.75 0 0 1 7.5 15Zm.75 2.25a.75.75 0 0 0 0 1.5H12a.75.75 0 0 0 0-1.5H8.25Z"
                                            clip-rule="evenodd"
                                        />
                                        <path
                                            d="M12.971 1.816A5.23 5.23 0 0 1 14.25 5.25v1.875c0 .207.168.375.375.375H16.5a5.23 5.23 0 0 1 3.434 1.279 9.768 9.768 0 0 0-6.963-6.963Z"
                                        />
                                    </svg>
                                </div>
                                <div class=" self-center flex-1">
                                    <div class=" font-semibold line-clamp-1">#{kb.title}</div>
                                </div>
                            </div>
                        </div>
                        <div class="flex flex-row space-x-1 self-center">
                            <button
                                class="self-center w-fit text-sm z-20 px-2 py-2 dark:text-gray-300 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
                                type="button"
                                aria-label={$i18n.t('Edit Knowledge Base')}
                                on:click={async (e) => {
                                    e.stopPropagation();
                                    goto('/admin/knowledge-bases/' + kb.id);
                                }}
                            >
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke-width="1.5"
                                    stroke="currentColor"
                                    class="w-4 h-4"
                                >
                                    <path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L6.832 19.82a4.5 4.5 0 01-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 011.13-1.897L16.863 4.487zm0 0L19.5 7.125"
                                    />
                                </svg>
                            </button>
                            <button
                                class="self-center w-fit text-sm px-2 py-2 dark:text-gray-300 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
                                type="button"
                                aria-label={$i18n.t('Delete Kb')}
                                on:click={(e) => {
                                    e.stopPropagation();
                                    showConfirmDeleteModal = true;
                                    deleteId = kb.id;
                                }}
                            >
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke-width="1.5"
                                    stroke="currentColor"
                                    class="w-4 h-4"
                                >
                                    <path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"
                                    />
                                </svg>
                            </button>
                        </div>
                    </button>
                {/each}
            </div>
		</div>
	</div>
</div>
