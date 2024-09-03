<script lang="ts">
	import { page } from '$app/stores';
    import { getContext, onMount, createEventDispatcher } from 'svelte';
	import { models, config, documents } from '$lib/stores';
	import { toast } from 'svelte-sonner';
    import { createNewDoc, deleteDocByName, getDocs } from '$lib/apis/documents';
    import Switch from '$lib/components/common/Switch.svelte';
    import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Checkbox from '$lib/components/common/Checkbox.svelte';
    import { getKnowledgeBaseById, saveKnowledgeBase } from '$lib/apis/configs';
	import { goto } from '$app/navigation';
	import { blobToFile, transformFileName } from '$lib/utils';
	import { uploadFile } from '$lib/apis/files';
	import { processDocToVectorDB, processWebDocToVectorDB } from '$lib/apis/rag';
	import AddDocModal from '$lib/components/documents/AddDocModal.svelte';
	import { transcribeAudio } from '$lib/apis/audio';
	import Dropdown from '$lib/components/common/Dropdown.svelte';
	import { DropdownMenu } from 'bits-ui';
	import { flyAndScale } from '$lib/utils/transitions';
	import AddWebsiteModal from '$lib/components/documents/AddWebsiteModal.svelte';

    const i18n = getContext('i18n');

    let kbId = $page.params.id;
    let selectedTab = 'documents';
    let knowledgeBase = {
        label: '',
        id: '',
        desc: '',
        docs: []
    };
    let search_doc_query = '';
    let showAddDocModal = false;
    let showAddWebsiteModal = false;

    $: filteredDocs = knowledgeBase.docs.filter((doc) => {
        return search_doc_query === '' || (doc.name.includes(search_doc_query) || doc.title.includes(search_doc_query) || doc.filename.includes(search_doc_query)) 
    });

    async function submitHandler(){
        updateKnowledgeBase(true);
    }

    const deleteDoc = async (name) => {
        knowledgeBase.docs = knowledgeBase.docs.filter((d) => d.name !== name);
        await updateKnowledgeBase();
		await deleteDocByName(localStorage.token, name);
		await documents.set(await getDocs(localStorage.token));
	};

    const uploadWebsite = async (url: string, tags?: object) => {
		const res = await processWebDocToVectorDB(localStorage.token, url).catch((error) => {
			toast.error(error);
			return null;
		});

		console.log({res})

		if (res) {
			for (const element of res){
				const createdDoc = await createNewDoc(
					localStorage.token,
					element.collection_name,
					element.filename,
					transformFileName(element.filename),
					element.filename,
					tags?.length > 0
						? 
						{
							tags: tags
						}
						: null
				).catch((error) => {
					toast.error(error);
                    console.error('error creating doc: ', error)
					return null;
				});
                
                if(createdDoc){
                    knowledgeBase.docs.push(createdDoc);
                }
			}
            await documents.set(await getDocs(localStorage.token));
            await updateKnowledgeBase();
		}
	};

    const uploadDoc = async (file, tags?: object) => {
		console.log(file);
		// Check if the file is an audio file and transcribe/convert it to text file
		if (['audio/mpeg', 'audio/wav', 'audio/ogg'].includes(file['type'])) {
			const transcribeRes = await transcribeAudio(localStorage.token, file).catch((error) => {
				toast.error(error);
				return null;
			});

			if (transcribeRes) {
				console.log(transcribeRes);
				const blob = new Blob([transcribeRes.text], { type: 'text/plain' });
				file = blobToFile(blob, `${file.name}.txt`);
			}
		}

		// Upload the file to the server
		const uploadedFile = await uploadFile(localStorage.token, file).catch((error) => {
			toast.error(error);
			return null;
		});

		const res = await processDocToVectorDB(localStorage.token, uploadedFile.id).catch((error) => {
			toast.error(error);
			return null;
		});

		if (res) {
			const createdDoc = await createNewDoc(
				localStorage.token,
				res.collection_name,
				res.filename,
				transformFileName(res.filename),
				res.filename,
				// tags?.length > 0
				// 	? {
				// 			tags: tags
				// 		}
				// 	: null
			).catch((error) => {
				toast.error(error);
				return null;
			});
			await documents.set(await getDocs(localStorage.token));
            if (createdDoc){
                knowledgeBase.docs.push(createdDoc)
                await updateKnowledgeBase();
            }
		}
	};

    const updateKnowledgeBase = async (showSuccessMessage: boolean = false) => {
        const res = await saveKnowledgeBase(localStorage.token, knowledgeBase).catch((e) => {
                console.error(e);
                toast.error($i18n.t('Failed to save knowledge base'));
            });

        if (res.kb) {
            knowledgeBase = res.kb;
            if(showSuccessMessage){
                toast.success($i18n.t('Knowledge base saved successfully'));
            }
        }
    }

    onMount(async () => {
        const res = await getKnowledgeBaseById(localStorage.token, kbId);

        if (res) {
            knowledgeBase = res;
        }
    })
</script>

<!-- TODO: add modal for existing files and upload files -->
<AddDocModal bind:show={showAddDocModal} {uploadDoc} />
<AddWebsiteModal bind:show={showAddWebsiteModal} {uploadWebsite} />

<div class="flex flex-col lg:flex-row w-full h-full py-2 lg:space-x-4">
    <div
        id="admin-knowledge-base-tabs-container"
        class="tabs flex flex-row overflow-x-auto space-x-1 max-w-full lg:space-x-0 lg:space-y-1 lg:flex-col lg:flex-none lg:w-44 dark:text-gray-200 text-xs text-left scrollbar-none"
    >
            <button
                class="px-2.5 py-2.5 min-w-fit rounded-lg flex-1 lg:flex-none flex text-right transition hover:bg-gray-50 dark:hover:bg-gray-850"
                on:click={() => {
                    goto('/admin/knowledge-bases');
                }}
            >
                <div class=" self-center mr-2">
                    <svg
                        viewBox="0 0 16 16"
                        fill="currentColor"
                        xmlns="http://www.w3.org/2000/svg"
                        class="w-4 h-4"
                    >
                        <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                        <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                        <g id="SVGRepo_iconCarrier">
                            <path
                                d="M3.5 7.5h10a0.5 0.5 0 1 1 0 1H3.5a0.5 0.5 0 0 1 0-1z"
                            ></path>
                            <path
                                d="m3.707 8 4.147 4.147a0.5 0.5 0 0 1-0.707 0.707l-4.5-4.5a0.5 0.5 0 0 1 0-0.707l4.5-4.5a0.5 0.5 0 1 1 0.707 0.707L3.707 8z"
                            ></path>
                        </g>
                    </svg>
                </div>
                <div class=" self-center">{$i18n.t('Back')}</div>
            </button>
            <button
                class="px-2.5 py-2.5 min-w-fit rounded-lg flex-1 lg:flex-none flex text-right transition {selectedTab ===
                'documents'
                    ? 'bg-gray-100 dark:bg-gray-800'
                    : ' hover:bg-gray-50 dark:hover:bg-gray-850'}"
                on:click={() => {
                    selectedTab = 'documents';
                }}
            >
                <div class=" self-center mr-2">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 16 16"
                        class="w-4 h-4"
                        fill="currentColor"
                    >
                        <path
                            fill-rule="evenodd"
                            d="M3.75 1c-.69 0-1.25.56-1.25 1.25v11.5c0 .69.56 1.25 1.25 1.25h8.5c.69 0 1.25-.56 1.25-1.25V8.5a2.5 2.5 0 0 0-2.5-2.5h-1.25a1.25 1.25 0 0 1-1.25-1.25V3.5A2.5 2.5 0 0 0 6 1H3.75ZM5 10a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5A.5.5 0 0 1 5 10Zm.5 1.5a.5.5 0 0 0 0 1H8a.5.5 0 0 0 0-1H5.5Z"
                            clip-rule="evenodd"
                        />
                        <path
                            d="M8.647 1.21a3.486 3.486 0 0 1 1.064 2.29v1.25c0 .138.112.25.25.25H11a3.486 3.486 0 0 1 2.29.852 6.512 6.512 0 0 0-4.643-4.643Z"
                        />
                    </svg>
                </div>
                <div class=" self-center">{$i18n.t('Documents')}</div>
            </button>
            <button
                class="px-2.5 py-2.5 min-w-fit rounded-lg flex-1 lg:flex-none flex text-right transition {selectedTab ===
                'general'
                    ? 'bg-gray-100 dark:bg-gray-800'
                    : ' hover:bg-gray-50 dark:hover:bg-gray-850'}"
                on:click={() => {
                    selectedTab = 'general';
                }}
            >
                <div class=" self-center mr-2">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 16 16"
                        fill="currentColor"
                        class="w-4 h-4"
                    >
                        <path
                            fill-rule="evenodd"
                            d="M6.955 1.45A.5.5 0 0 1 7.452 1h1.096a.5.5 0 0 1 .497.45l.17 1.699c.484.12.94.312 1.356.562l1.321-1.081a.5.5 0 0 1 .67.033l.774.775a.5.5 0 0 1 .034.67l-1.08 1.32c.25.417.44.873.561 1.357l1.699.17a.5.5 0 0 1 .45.497v1.096a.5.5 0 0 1-.45.497l-1.699.17c-.12.484-.312.94-.562 1.356l1.082 1.322a.5.5 0 0 1-.034.67l-.774.774a.5.5 0 0 1-.67.033l-1.322-1.08c-.416.25-.872.44-1.356.561l-.17 1.699a.5.5 0 0 1-.497.45H7.452a.5.5 0 0 1-.497-.45l-.17-1.699a4.973 4.973 0 0 1-1.356-.562L4.108 13.37a.5.5 0 0 1-.67-.033l-.774-.775a.5.5 0 0 1-.034-.67l1.08-1.32a4.971 4.971 0 0 1-.561-1.357l-1.699-.17A.5.5 0 0 1 1 8.548V7.452a.5.5 0 0 1 .45-.497l1.699-.17c.12-.484.312-.94.562-1.356L2.629 4.107a.5.5 0 0 1 .034-.67l.774-.774a.5.5 0 0 1 .67-.033L5.43 3.71a4.97 4.97 0 0 1 1.356-.561l.17-1.699ZM6 8c0 .538.212 1.026.558 1.385l.057.057a2 2 0 0 0 2.828-2.828l-.058-.056A2 2 0 0 0 6 8Z"
                            clip-rule="evenodd"
                        />
                    </svg>
                </div>
                <div class=" self-center">{$i18n.t('General')}</div>
            </button>
    </div>
    <div class="flex-1 mt-3 lg:mt-0 overflow-y-scroll">
        <form
            class="flex flex-col w-full h-full dark:text-gray-300 px-5 pt-4 pb-0.5"
            id="knowledge-base-form"
            on:submit|preventDefault={() => {
                submitHandler();
            }}
        >
        <div class="space-y-3 overflow-y-scroll scrollbar-hidden h-full">
            {#if selectedTab === 'general'}
                <div class="flex w-full gap-2 mt-2">
                    <div class="w-full">
                        <div class=" self-center text-xs font-medium min-w-fit mb-1">
                            {$i18n.t('Label')}
                        </div>
                        <input
                            class="w-full rounded-lg py-2 px-4 text-sm border dark:border-gray-600
                            dark:bg-gray-900 outline-none"
                            placeholder={$i18n.t('Enter profile label')}
                            id="knowledge-base-label"
                            aria-label="knowledge-base-label"
                            bind:value={knowledgeBase.label}
                        />
                    </div>
                    <div class="w-full"></div>
                </div>
            
                <div class="flex w-full gap-2 mt-2">
                    <div class="w-full">
                        <div class=" self-center text-xs font-medium min-w-fit mb-1">
                            {$i18n.t('Description')}
                        </div>
                        <textarea
                            class="px-3 py-1.5 text-sm w-full bg-transparent border dark:border-gray-600 outline-none rounded-lg"
                            rows="4"
                            placeholder={$i18n.t('Enter description')}
                            id="knowledge-base-description"
                            aria-label="knowledge-base-description"
                            bind:value={knowledgeBase.desc}
                        />
                    </div>
                </div>
            {:else if selectedTab === 'documents'}
                <div class="flex w-full gap-2 mt-2">
                    <div class="w-full">
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
                                    bind:value={search_doc_query}
                                    id="search-doc-input"
                                    aria-label="search-doc-input"
                                    placeholder={$i18n.t('Search Documents')}
                                />
                            </div>
                        
                            <div>
                                <Dropdown>
                                    <Tooltip content={$i18n.t('More')}>
                                        <button
                                            class=" px-2 py-2 rounded-xl border border-gray-200 dark:border-gray-600 dark:border-0 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 transition font-medium text-sm flex items-center space-x-1"
                                            aria-label={$i18n.t('More')}
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
                                    </Tooltip>
                                    <div slot="content">
                                        <DropdownMenu.Content
                                        class="w-full max-w-[200px] rounded-xl px-1 py-1  border-gray-300/30 dark:border-gray-700/50 z-50 bg-white dark:bg-gray-850 dark:text-white shadow"
                                        sideOffset={15}
                                        alignOffset={-8}
                                        side="left"
                                        align="start"
                                        transition={flyAndScale}
                                        >
                                            <DropdownMenu.Item
                                                class="flex gap-2 items-center px-3 py-2 text-sm  font-medium cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800  rounded-xl"
                                                on:click={() => {
                                                    showAddDocModal = true;
                                                }}
                                            >
                                                <!-- <DocumentArrowUpSolid /> -->
                                                <div class=" line-clamp-1">{$i18n.t('Upload Files')}</div>
                                            </DropdownMenu.Item>
                                            <DropdownMenu.Item
                                                class="flex gap-2 items-center px-3 py-2 text-sm  font-medium cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800  rounded-xl"
                                                on:click={() => {
                                                    showAddWebsiteModal = true;
                                                }}
                                            >
                                                <div class=" line-clamp-1">{$i18n.t('Upload Websites')}</div>
                                            </DropdownMenu.Item>
                                        </DropdownMenu.Content>
                                    </div>
                                </Dropdown>
                            </div>
                        </div>
                        {#each filteredDocs as doc}
                            <button
                                class=" flex space-x-4 cursor-pointer text-left w-full px-3 py-2 dark:hover:bg-white/5 hover:bg-black/5 rounded-xl"
                                type="button"
                                on:click={() => {
                                    if (doc?.selected === 'checked') {
                                        doc.selected = 'unchecked';
                                    } else {
                                        doc.selected = 'checked';
                                    }
                                }}
                            >
                                <div class="my-auto flex items-center">
                                    <Checkbox state={doc?.selected ?? 'unchecked'} />
                                </div>
                                <div class=" flex flex-1 space-x-4 cursor-pointer w-full">
                                    <div class=" flex items-center space-x-3">
                                        <div class="p-2.5 bg-red-400 text-white rounded-lg">
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
                                            <div class=" font-semibold line-clamp-1">#{doc.name} ({doc.filename})</div>
                                            <div class=" text-xs overflow-hidden text-ellipsis line-clamp-1">
                                                {doc.title}
                                            </div>
                                        </div>


                                    </div>
                                </div>

                                <div class="flex flex-row space-x-1 self-center">
                                    <button
                                        class="self-center w-fit text-sm px-2 py-2 dark:text-gray-300 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
                                        type="button"
                                        aria-label={$i18n.t('Delete Doc')}
                                        on:click={(e) => {
                                            e.stopPropagation();
                                            deleteDoc(doc.name);
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
            {/if}
        </div>

        {#if selectedTab === 'general'}
            <div class="flex justify-end pt-3 text-sm font-medium">
                <button
                    class=" px-4 py-2 bg-emerald-700 hover:bg-emerald-800 text-gray-100 transition rounded-lg"
                    type="submit"
                    id="save-knowledge-base"
                >
                    {$i18n.t('Save')}
                </button>
            </div>
        {/if}
        </form>
    </div>
</div>
