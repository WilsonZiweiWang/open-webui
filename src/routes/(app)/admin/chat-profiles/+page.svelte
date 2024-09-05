<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { config, user } from '$lib/stores';
	import { toast } from 'svelte-sonner';
    import { getAllChatProfiles, saveChatProfile, addChatProfile, deleteChatProfile } from '$lib/apis/configs';
	import ConfirmDeleteModal from '../../../../lib/components/admin/ConfirmDeleteModal.svelte';
	import { goto } from '$app/navigation';
    import Modal from '$lib/components/common/Modal.svelte';

    const i18n = getContext('i18n');

    let showAddProfileModal = false;
    let showConfirmDeleteModal = false;
    let deleteId = '';

    let initProfile = {
        label: '',
        id: '',
        roles_allowed: ['user'],
        enabled: true,
        params: {
            system: ''
        },
        files: []
    };

    let newProfilelabel = '';
    let profiles: any[] = [];

    let query = '';

    $: filteredProfiles = profiles.filter(profile => {
        return (query === '' || profile.label.includes(query));
    })

    async function fetchProfiles() {
        const res = await getAllChatProfiles(localStorage.token).catch((e) => {
            console.error(e);
            toast.error($i18n.t('Failed to fetch chat profiles'));
        });

        if (res) {
            profiles = res;
        }
    }

    $: if(!showAddProfileModal) {
        newProfilelabel = '';
    }

    async function deleteProfile(profileId: string) {
        console.log('delete profile', profileId);
        if(!profileId) return;

        const res = await deleteChatProfile(localStorage.token, profileId).catch((e) => {
            console.error(e);
            toast.error($i18n.t('Failed to delete Chat Profile'));
        });

        if (res) {
            toast.success($i18n.t('Chat Profile deleted successfully'));
            await fetchProfiles();
        }
    }

    const handleAddChatProfile = async (label: string) => {
        const profile = {
            ...initProfile,
            label
        }

        const res = await addChatProfile(localStorage.token, profile).catch((e) => {
                console.error(e);
                toast.error($i18n.t('Failed to add chat profile'));
        });

        if (res.profile_id) {
            toast.success($i18n.t('New chat profile added successfully'));
            goto('/admin/chat-profiles/' + res.profile_id); 
            await fetchProfiles();
        }
    }

	onMount(async () => {
        await fetchProfiles();
	});
</script>

<Modal bind:show={showAddProfileModal} size="sm">
    <div class=" flex justify-between dark:text-gray-300 px-5 pt-4 pb-0.5">
        <div class=" text-lg font-medium self-center">{$i18n.t('Add Profile')}</div>
        <button
            class="self-center"
            on:click={() => {
                showAddProfileModal = false;
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
                {$i18n.t('Label')}
            </div>
            <input
                class="w-full rounded-lg py-2 px-4 text-sm border dark:border-gray-600
                dark:bg-gray-900 bg-gray-50 outline-none"
                placeholder={$i18n.t('Enter profile label')}
                bind:value={newProfilelabel}
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
                            showAddProfileModal = false;
                        }}
                    >
                        {$i18n.t('Cancel')}
                    </button>
                    <button
                        class=" self-center flex items-center gap-1 px-3.5 py-2 rounded-xl text-sm font-medium bg-green-400 hover:bg-green-300 text-white"
                        on:click={() => {
                            handleAddChatProfile(newProfilelabel);
                            showAddProfileModal = false;
                        }}
                    >
                        {$i18n.t('Add')}
                    </button>
                </div>
            </div>
        </div>
    </div>
</Modal>

<ConfirmDeleteModal bind:show={showConfirmDeleteModal} title="Delete this chat profile?" on:confirm={() => deleteProfile(deleteId)}/>

<div
	class="flex flex-col h-full justify-between space-y-3 text-sm"
>
	<div class=" space-y-3 overflow-y-scroll scrollbar-hidden h-full">
		<div>
            
			<div class=" mb-2 text-sm font-medium">{$i18n.t('Chat Profiles')}</div>
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
                        placeholder={$i18n.t('Search Profiles')}
                    />
                </div>
            
                <div>
                    <button
                        class=" px-2 py-2 rounded-xl border border-gray-200 dark:border-gray-600 dark:border-0 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 transition font-medium text-sm flex items-center space-x-1"
                        aria-label={$i18n.t('Add Profile')}
                        type="button"
                        on:click={() => {
                            showAddProfileModal = true;
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
                {#each filteredProfiles as profile}
                    <button
                        class=" flex space-x-4 cursor-pointer text-left w-1/2 px-3 py-2 dark:hover:bg-white/5 hover:bg-black/5 rounded-xl"
                        type="button"
                        on:click={() => {
                            goto('/admin/chat-profiles/' + profile.id);
                        }}
                    >
                        <div class=" flex flex-1 space-x-4 cursor-pointer w-full">
                            <div class=" flex items-center space-x-3">
                                <div class="p-2.5 bg-red-400 text-white rounded-lg">
                                    <svg width="24px" height="24px" viewBox="0 0 24 24" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" fill="#ffffff">
                                        <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                                        <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                                        <g id="SVGRepo_iconCarrier">
                                          <title>profile_line</title>
                                          <g id="页面-1" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
                                            <g id="File" transform="translate(0.000000, -288.000000)">
                                              <g id="profile_line" transform="translate(0.000000, 288.000000)">
                                                <path d="M24,0 L24,24 L0,24 L0,0 L24,0 Z M12.5934901,23.257841 L12.5819402,23.2595131 L12.5108777,23.2950439 L12.4918791,23.2987469 L12.4918791,23.2987469 L12.4767152,23.2950439 L12.4056548,23.2595131 C12.3958229,23.2563662 12.3870493,23.2590235 12.3821421,23.2649074 L12.3780323,23.275831 L12.360941,23.7031097 L12.3658947,23.7234994 L12.3769048,23.7357139 L12.4804777,23.8096931 L12.4953491,23.8136134 L12.4953491,23.8136134 L12.5071152,23.8096931 L12.6106902,23.7357139 L12.6232938,23.7196733 L12.6232938,23.7196733 L12.6266527,23.7031097 L12.609561,23.275831 C12.6075724,23.2657013 12.6010112,23.2592993 12.5934901,23.257841 L12.5934901,23.257841 Z M12.8583906,23.1452862 L12.8445485,23.1473072 L12.6598443,23.2396597 L12.6498822,23.2499052 L12.6498822,23.2499052 L12.6471943,23.2611114 L12.6650943,23.6906389 L12.6699349,23.7034178 L12.6699349,23.7034178 L12.678386,23.7104931 L12.8793402,23.8032389 C12.8914285,23.8068999 12.9022333,23.8029875 12.9078286,23.7952264 L12.9118235,23.7811639 L12.8776777,23.1665331 C12.8752882,23.1545897 12.8674102,23.1470016 12.8583906,23.1452862 L12.8583906,23.1452862 Z M12.1430473,23.1473072 C12.1332178,23.1423925 12.1221763,23.1452606 12.1156365,23.1525954 L12.1099173,23.1665331 L12.0757714,23.7811639 C12.0751323,23.7926639 12.0828099,23.8018602 12.0926481,23.8045676 L12.108256,23.8032389 L12.3092106,23.7104931 L12.3186497,23.7024347 L12.3186497,23.7024347 L12.3225043,23.6906389 L12.340401,23.2611114 L12.337245,23.2485176 L12.337245,23.2485176 L12.3277531,23.2396597 L12.1430473,23.1473072 Z" id="MingCute" fill-rule="nonzero">
                                                </path>
                                                <path d="M20,3 C21.1046,3 22,3.89543 22,5 L22,19 C22,20.1046 21.1046,21 20,21 L4,21 C2.89543,21 2,20.1046 2,19 L2,5 C2,3.89543 2.89543,3 4,3 L20,3 Z M20,5 L4,5 L4,19 L20,19 L20,5 Z M17,15 C17.5523,15 18,15.4477 18,16 C18,16.51285 17.613973,16.9355092 17.1166239,16.9932725 L17,17 L7,17 C6.44772,17 6,16.5523 6,16 C6,15.48715 6.38604429,15.0644908 6.88337975,15.0067275 L7,15 L17,15 Z M10,7 C11.1046,7 12,7.89543 12,9 L12,11 C12,12.1046 11.1046,13 10,13 L8,13 C6.89543,13 6,12.1046 6,11 L6,9 C6,7.89543 6.89543,7 8,7 L10,7 Z M17,11 C17.5523,11 18,11.4477 18,12 C18,12.5523 17.5523,13 17,13 L14,13 C13.4477,13 13,12.5523 13,12 C13,11.4477 13.4477,11 14,11 L17,11 Z M10,9 L8,9 L8,11 L10,11 L10,9 Z M17,7 C17.5523,7 18,7.44772 18,8 C18,8.51283143 17.613973,8.93550653 17.1166239,8.9932722 L17,9 L14,9 C13.4477,9 13,8.55228 13,8 C13,7.48716857 13.386027,7.06449347 13.8833761,7.0067278 L14,7 L17,7 Z" id="形状" fill="#ffffff">
                                                </path>
                                              </g>
                                            </g>
                                          </g>
                                        </g>
                                    </svg>
                                </div>
                                <div class=" self-center flex-1">
                                    <div class=" font-semibold line-clamp-1">#{profile.label}</div>
                                    <!-- <div class=" text-xs overflow-hidden text-ellipsis line-clamp-1">
                                        {profile.roles_allowed.join(', ')}
                                    </div> -->
                                </div>
                            </div>
                        </div>
                        <div class="flex flex-row space-x-1 self-center">
                            <button
                                class="self-center w-fit text-sm z-20 px-2 py-2 dark:text-gray-300 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
                                type="button"
                                aria-label={$i18n.t('Edit Profile')}
                                on:click={async (e) => {
                                    e.stopPropagation();
                                    goto('/admin/chat-profiles/' + profile.id);
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
                                aria-label={$i18n.t('Delete Profile')}
                                on:click={(e) => {
                                    e.stopPropagation();
                                    showConfirmDeleteModal = true;
                                    deleteId = profile.id;
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
