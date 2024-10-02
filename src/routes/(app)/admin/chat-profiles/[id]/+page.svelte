<script lang="ts">
	import { page } from '$app/stores';
    import { getContext, onMount } from 'svelte';
	import { user, models } from '$lib/stores';
	import { toast } from 'svelte-sonner';
    import Switch from '$lib/components/common/Switch.svelte';
    import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Checkbox from '$lib/components/common/Checkbox.svelte';
    import { getChatProfileById, getKnowledgeBases, saveChatProfile } from '$lib/apis/configs';
	import { goto } from '$app/navigation';
	import AdjustmentsHorizontal from '$lib/components/icons/AdjustmentsHorizontal.svelte';
	import Modal from '$lib/components/common/Modal.svelte';
	import AdvancedParams from '$lib/components/chat/Settings/Advanced/AdvancedParams.svelte';
	import Selector from '$lib/components/chat/ModelSelector/Selector.svelte';

    const i18n = getContext('i18n');

    let selectedTab = 'general';
    let profileId = $page.params.id;
    let profile = {
        id: '',
        title: '',
        description: '',
        roles_allowed: [],
        llm_model: '',
        knowledge_bases: [],
        enabled: true,
        params: {
            system: '',
		    // Advanced
            seed: null,
            stop: null,
            temperature: null,
            frequency_penalty: null,
            repeat_last_n: null,
            mirostat: null,
            mirostat_eta: null,
            mirostat_tau: null,
            top_k: null,
            top_p: null,
            min_p: null,
            tfs_z: null,
            num_ctx: null,
            num_batch: null,
            num_keep: null,
            max_tokens: null,
            use_mmap: null,
            use_mlock: null,
            num_thread: null,
            num_gpu: null,
            template: null
        },
    };
    let roles = ['user'];
    let search_kb_query = '';

    let showAddModal = false;
    let allKnowledgeBases = [];
    let profileKnowledgeBases = []; // To contain the entire information instead of just the ID

    $: filteredKbs = profileKnowledgeBases.filter((kb) => {
        return search_kb_query === '' || kb.title.toLowerCase().includes(search_kb_query.toLowerCase());
    });

    // $: if(showAddModal) {
    //     fetchKnowledgeBases();
    // }

    $: modalKnowledgeBases = allKnowledgeBases.filter((kb) => {
                    return !profile.knowledge_bases.some((id) => id === kb.id);
        }).map((kb) => {
            return {
                ...kb,
                selected: 'unchecked'
            }
        });

    async function submitHandler(){
        if(profile.id === ''){
            console.error('Profile ID is missing');
            return;
        }

        const res = await saveChatProfile(localStorage.token, profile).catch((e) => {
            console.error(e);
            toast.error($i18n.t('Failed to save Chat Profile'));
        });

        if (res) {
            profile = res;
            toast.success($i18n.t('Chat Profile saved successfully'));
        }
    }

    async function fetchKnowledgeBases() {
        const res = await getKnowledgeBases(localStorage.token).catch((e) => {
            console.error(e);
            toast.error($i18n.t('Failed to fetch knowledge bases'));
        });

        if (res) {
            allKnowledgeBases = res;
            profileKnowledgeBases = [];
            for (const kb_id of profile.knowledge_bases) {
                const kb = allKnowledgeBases.find((kb) => kb.id === kb_id);
                if (kb) {
                    profileKnowledgeBases.push(kb);
                }
            }
        }
    }

    const handleAddKnowledgeBaseToProfile = async () => {
        const selectedKbs = modalKnowledgeBases.filter((kb) => kb.selected === 'checked')

        for (const kb of selectedKbs){
            if (profile.knowledge_bases.includes(kb.id)){
                toast.error($i18n.t(`Knowledge base ${kb.title} with id ${kb.id} is already added`));
                return;
            }
        }

        profile.knowledge_bases = [...profile.knowledge_bases, ...selectedKbs.map((kb) => kb.id)];
        profileKnowledgeBases = [...profileKnowledgeBases, ...selectedKbs.map((kb) => {
            kb.selected = 'unchecked';
            return kb;
        })];
    }

    onMount(async () => {
        const res = await getChatProfileById(localStorage.token, profileId);

        if (res) {
            profile = res;
        }

        await fetchKnowledgeBases();
    })
</script>

<Modal bind:show={showAddModal} size="md">
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
        <div class="w-full flex flex-wrap">
            {#if modalKnowledgeBases.length === 0}
                <div class="w-full text-center dark:text-gray-300">{$i18n.t('No knowledge bases available')}</div>
            {:else}
                {#each modalKnowledgeBases as kb}
                    <button
                        class=" flex space-x-4 cursor-pointer text-left w-1/2 px-3 py-2 dark:hover:bg-white/5 hover:bg-black/5 rounded-xl"
                        type="button"
                        on:click={() => {
                            if (kb?.selected === 'checked') {
                                kb.selected = 'unchecked';
                            } else {
                                kb.selected = 'checked';
                            }
                        }}
                    >
                        <div class="my-auto flex items-center">
                            <Checkbox state={kb?.selected ?? 'unchecked'} />
                        </div>
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
                    </button>
                {/each}
            {/if}
        </div>
    </div>

    <div class="px-5 pt-4 pb-5 w-full">
        <div class="flex justify-end">
            <div class="flex  items-end space-x-1 mt-1.5">
                <div class="flex justify-end gap-1">
                    {#if modalKnowledgeBases.length > 0}
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
                                handleAddKnowledgeBaseToProfile()
                                showAddModal = false;
                            }}
                        >
                            {$i18n.t('Add')}
                        </button>
                    {/if}
                </div>
            </div>
        </div>
    </div>
</Modal>

<div class="flex flex-col lg:flex-row w-full h-full py-2 lg:space-x-4">
    <div
        id="admin-chat-profiles-tabs-container"
        class="tabs flex flex-row overflow-x-auto space-x-1 max-w-full lg:space-x-0 lg:space-y-1 lg:flex-col lg:flex-none lg:w-44 dark:text-gray-200 text-xs text-left scrollbar-none"
    >
            <button
                class="px-2.5 py-2.5 min-w-fit rounded-lg flex-1 lg:flex-none flex text-right transition hover:bg-gray-50 dark:hover:bg-gray-850"
                on:click={() => {
                    goto('/admin/chat-profiles');
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
            <button
                class="px-2.5 py-2.5 min-w-fit rounded-lg flex-1 lg:flex-none flex text-right transition {selectedTab ===
                'knowledge-base'
                    ? 'bg-gray-100 dark:bg-gray-800'
                    : ' hover:bg-gray-50 dark:hover:bg-gray-850'}"
                on:click={() => {
                    selectedTab = 'knowledge-base';
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
                <div class=" self-center">{$i18n.t('Knowledge Bases')}</div>
            </button>
            <button
                class="px-2.5 py-2.5 min-w-fit rounded-lg flex-1 lg:flex-none flex text-right transition {selectedTab ===
                'params'
                    ? 'bg-gray-100 dark:bg-gray-800'
                    : ' hover:bg-gray-50 dark:hover:bg-gray-850'}"
                on:click={() => {
                    selectedTab = 'params';
                }}
            >
                <div class=" self-center mr-2">
                    <AdjustmentsHorizontal strokeWidth="0.5" />
                </div>
                <div class=" self-center">{$i18n.t('Params')}</div>
            </button>
    </div>
    <div class="flex-1 mt-3 lg:mt-0 overflow-y-scroll">
        <form
            class="flex flex-col w-full h-full dark:text-gray-300 px-5 pt-4 pb-0.5"
            id="chat-profile-form"
            on:submit|preventDefault={() => {
                submitHandler();
            }}
        >
            <div class="space-y-3 overflow-y-scroll scrollbar-hidden h-full">
                {#if selectedTab === 'general'}
                    <div class="flex w-full gap-2 mt-2">
                        <div class="w-full">
                            <div class=" self-center text-xs font-medium min-w-fit mb-1">
                                {$i18n.t('Title')}
                            </div>
                            <input
                                class="w-full rounded-lg py-2 px-4 text-sm border dark:border-gray-600
                                dark:bg-gray-900 outline-none"
                                placeholder={$i18n.t('Enter profile title')}
                                bind:value={profile.title}
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
                                id="chat-profile-description"
                                aria-label="chat-profile-description"
                                bind:value={profile.description}
                            />
                        </div>
                    </div>
                
                    <div class="flex w-full gap-2 mt-2">
                        <div class="w-full">
                            <Tooltip
                                content={$i18n.t('Roles allowed to use this profile')}
                                placement="top-start"
                            >
                                <div class=" self-center text-xs font-medium min-w-fit mb-1">
                                    {$i18n.t('Roles Allowed')}
                                </div>
                            </Tooltip>
                            <button 
                                class="my-auto flex items-center w-full py-2 px-4 mb-1 text-sm dark:text-gray-300 dark:bg-gray-850 dark:hover:bg-gray-800 dark:hover:bg-white/5 hover:bg-black/5 rounded-xl cursor-pointer outline-none"
                                type="button"
                                on:click={() => {
                                    if(profile.roles_allowed.length === roles.length) {
                                        profile.roles_allowed = [];
                                    } else {
                                        profile.roles_allowed = roles;
                                    }
                                }}
                            >
                                <Checkbox 
                                    state={profile.roles_allowed.length === roles.length ? 'checked' : 'unchecked'}>
                                </Checkbox>
                                <div class="px-2">
                                    {$i18n.t('All')}
                                </div>
                            </button>
                            {#each roles as role}
                                <button 
                                    class="my-auto flex items-center w-full py-2 px-4 mb-1 text-sm dark:text-gray-300 dark:bg-gray-850 dark:hover:bg-gray-800 dark:hover:bg-white/5 hover:bg-black/5 rounded-xl cursor-pointer outline-none"
                                    type="button"
                                    on:click={() => {
                                        if (profile.roles_allowed.includes(role)) {
                                            profile.roles_allowed = profile.roles_allowed.filter((r) => r !== role);
                                        } else {
                                            profile.roles_allowed = [...profile.roles_allowed, role];
                                        }
                                    }} 
                                >
                                    <Checkbox 
                                        state={profile.roles_allowed.includes(role) ? 'checked' : 'unchecked'}>
                                    </Checkbox>
                                    <div class="px-2">
                                        {role}
                                    </div>
                                </button>
                            {/each}
                        </div>
                    </div>
                    
                    <div class="flex justify-between items-center text-sm mt-2">
                        <Tooltip content={$i18n.t("If disabled, this profile can't be used to create a chat")} placement="top-start">
                            <div class="  font-medium">{$i18n.t('Enable')}</div>
                        </Tooltip>
                        <div class="mt-1">
                            <Switch
                                bind:state={profile.enabled}
                            />
                        </div>
                    </div>
                    
                {:else if selectedTab === 'params'}
                    <div class="flex w-full gap-2 mt-2">
                        <div class="w-full">
                            <div class=" self-center text-xs font-medium min-w-fit mb-1">
                                {$i18n.t('LLM Model')}
                            </div>
                            <Selector
                                placeholder={$i18n.t('Select a model')}
                                items={$models.map((model) => ({
                                    value: model.id,
                                    label: model.name,
                                    model: model
                                }))}
                                showTemporaryChatControl={false}
                                bind:value={profile.llm_model}
                            />
                            <div class=" self-center text-xs font-medium min-w-fit mb-1">
                                {$i18n.t('System Prompt')}
                            </div>
                            <textarea
                                class="px-3 py-1.5 text-sm w-full bg-transparent border dark:border-gray-600 outline-none rounded-lg"
                                placeholder={`Write your model system prompt content here\ne.g.) You are Mario from Super Mario Bros, acting as an assistant.`}
                                rows="4"
                                bind:value={profile.params.system}
                            />

                            <AdvancedParams admin={$user?.role === 'admin'} bind:params={profile.params} />
                        </div>
                    </div>
                {:else if selectedTab === 'knowledge-base'}
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
                                        bind:value={search_kb_query}
                                        id="search-doc-input"
                                        aria-label="search-doc-input"
                                        placeholder={$i18n.t('Search Knowledge Base')}
                                    />
                                </div>
                            
                                <div>
                                    <button
                                        class=" px-2 py-2 rounded-xl border border-gray-200 dark:border-gray-600 dark:border-0 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 transition font-medium text-sm flex items-center space-x-1"
                                        aria-label={$i18n.t('Add knowledge base')}
                                        type="button"
                                        on:click={() => {
                                            showAddModal = true;
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
                            {#each filteredKbs as kb}
                                <button
                                    class=" flex space-x-4 cursor-pointer text-left w-full px-3 py-2 dark:hover:bg-white/5 hover:bg-black/5 rounded-xl"
                                    type="button"
                                    on:click={() => {
                                        if (kb?.selected === 'checked') {
                                            kb.selected = 'unchecked';
                                        } else {
                                            kb.selected = 'checked';
                                        }
                                    }}
                                >
                                    <div class="my-auto flex items-center">
                                        <Checkbox state={kb?.selected ?? 'unchecked'} />
                                    </div>
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
                                            aria-label={$i18n.t('Go to knowledge base')}
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
                                            aria-label={$i18n.t('Remove knowledge base from this profile')}
                                            on:click={(e) => {
                                                e.stopPropagation();
                                                profile.knowledge_bases = profile.knowledge_bases.filter((id) => id !== kb.id);
                                                profileKnowledgeBases = profileKnowledgeBases.filter((_kb) => _kb.id !== kb.id);
                                            }}
                                        >
                                        <svg
                                            xmlns="http://www.w3.org/2000/svg"
                                            viewBox="0 0 16 16"
                                            fill="currentColor"
                                            class="w-4 h-4"
                                        >
                                            <path
                                                d="M5.02 4.18a.75.75 0 0 0-1.06 1.06L7.15 8 3.96 11.18a.75.75 0 0 0 1.06 1.06L8 9.06l3.18 3.18a.75.75 0 0 0 1.06-1.06L8.94 8l3.18-3.18a.75.75 0 0 0-1.06-1.06L8 6.94 5.02 4.18z"
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

            <div class="flex justify-end pt-3 text-sm font-medium">
                <button
                    class=" px-4 py-2 bg-emerald-700 hover:bg-emerald-800 text-gray-100 transition rounded-lg"
                    type="submit"
                    id="save-chat-profile"
                >
                    {$i18n.t('Save')}
                </button>
            </div>
        </form>

    </div>
</div>
