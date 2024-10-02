import { WEBUI_API_BASE_URL } from '$lib/constants';
import type { Banner } from '$lib/types';

export const importConfig = async (token: string, config) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/configs/import`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify({
			config: config
		})
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.log(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const exportConfig = async (token: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/configs/export`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.log(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const setDefaultModels = async (token: string, models: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/configs/default/models`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify({
			models: models
		})
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.log(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const setDefaultPromptSuggestions = async (token: string, promptSuggestions: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/configs/default/suggestions`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify({
			suggestions: promptSuggestions
		})
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.log(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getBanners = async (token: string): Promise<Banner[]> => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/configs/banners`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.log(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const setBanners = async (token: string, banners: Banner[]) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/configs/banners`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify({
			banners: banners
		})
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.log(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};


export const getAllChatProfiles = async (token: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/chat-profiles/info`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.log(err);
			error = err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getFilteredChatProfiles = async (token: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/chat-profiles/filtered`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.log(err);
			error = err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getChatProfileById = async (token: string, profile_id: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/chat-profiles/${profile_id}`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.log(err);
			error = err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const saveChatProfile = async (token: string, profile) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/chat-profiles/update/${profile.id}`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify({
			title: profile.title,
			description: profile.description,
			roles_allowed: profile.roles_allowed,
			llm_model: profile.llm_model,
			knowledge_bases: profile.knowledge_bases,
			enabled: profile.enabled,
			params: profile.params
		})
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.log(err);
			error = err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const addChatProfile = async (token: string, profile) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/chat-profiles/add`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify(profile)
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.log(err);
			error = err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const deleteChatProfile = async (token: string, profile_id: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/chat-profiles/${profile_id}`, {
		method: 'DELETE',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.log(err);
			error = err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getKnowledgeBases = async (token: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/knowledge-bases`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.log(err);
			error = err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
}

export const getKnowledgeBaseById = async (token: string, kb_id: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/knowledge-bases/${kb_id}`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.log(err);
			error = err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const saveKnowledgeBase = async (token: string, kb) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/knowledge-bases/update/${kb.id}`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify(kb)
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.log(err);
			error = err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const addKnowledgeBase = async (token: string, kb) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/knowledge-bases/add`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify(kb)
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.log(err);
			error = err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const deleteKnowledgeBase = async (token: string, kb_id: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/knowledge-bases/${kb_id}`, {
		method: 'DELETE',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.log(err);
			error = err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
}; 