import { v } from "convex/values";
import { query, mutation, action } from "./_generated/server";
import { api } from "./_generated/api";
import { v4 as uuidv4 } from 'uuid';

// Write your Convex functions in any file inside this directory (`convex`).
// See https://docs.convex.dev/functions for more.

// You can read data from the database via a query:
// export const listNumbers = query({
//   // Validators for arguments.
//   args: {
//     count: v.number(),
//   },

//   // Query implementation.
//   handler: async (ctx, args) => {
//     //// Read the database as many times as you need here.
//     //// See https://docs.convex.dev/database/reading-data.
//     const numbers = await ctx.db
//       .query("numbers")
//       // Ordered by _creationTime, return most recent
//       .order("desc")
//       .take(args.count);
//     return {
//       viewer: (await ctx.auth.getUserIdentity())?.name ?? null,
//       numbers: numbers.reverse().map((number) => number.value),
//     };
//   },
// });

// // You can write data to the database via a mutation:
// export const addNumber = mutation({
//   // Validators for arguments.
//   args: {
//     value: v.number(),
//   },

//   // Mutation implementation.
//   handler: async (ctx, args) => {
//     //// Insert or modify documents in the database here.
//     //// Mutations can also read from the database like queries.
//     //// See https://docs.convex.dev/database/writing-data.

//     const id = await ctx.db.insert("numbers", { value: args.value });

//     console.log("Added new document with id:", id);
//     // Optionally, return a value from your mutation.
//     // return id;
//   },
// });

// // You can fetch data from and send data to third-party APIs via an action:
// export const myAction = action({
//   // Validators for arguments.
//   args: {
//     first: v.number(),
//     second: v.string(),
//   },

//   // Action implementation.
//   handler: async (ctx, args) => {
//     //// Use the browser-like `fetch` API to send HTTP requests.
//     //// See https://docs.convex.dev/functions/actions#calling-third-party-apis-and-using-npm-packages.
//     // const response = await ctx.fetch("https://api.thirdpartyservice.com");
//     // const data = await response.json();

//     //// Query data by running Convex queries.
//     const data = await ctx.runQuery(api.myFunctions.listNumbers, {
//       count: 10,
//     });
//     console.log(data);

//     //// Write data by running Convex mutations.
//     await ctx.runMutation(api.myFunctions.addNumber, {
//       value: args.first,
//     });
//   },
// });

export const createGame = mutation({
	args: {
		rounds: v.number(),
		time_per_round: v.number(),
	},
	handler: async (ctx, args) => {
		// Generate a uuid
		const game_id = uuidv4();
		// Generate a share code
		let code = ''
		const digits = '0123456789'
		for (let i = 0; i < 6; i++) {
			const random_index = Math.floor(Math.random() * digits.length)
			code += digits[random_index]
		}
		const max = 10; // Set this to the number of available images
		const numbers = Array.from({ length: max }, (_, i) => i + 1)
		for (let i = numbers.length; i > 0; i--) {
			const j = Math.floor(Math.random() * (i + 1));
			[numbers[i], numbers[j]] = [numbers[j], numbers[i]]
		}
		const images = numbers.slice(0, args.rounds)
		await ctx.db.insert("games", {
			game_id: game_id,
			rounds: args.rounds,
			time_per_round: args.time_per_round,
			player_ids: [],
			creator_id: '',
			share_code: code,
			images: images,
			status: 0,
			answers: [],
			step: 0
		})
		return game_id;
	}
})

export const createPlayer = mutation({
	args: {
		display_name: v.string()
	},
	handler: async (ctx, args) => {
		const player_id = uuidv4();
		const display_name = args.display_name;
		await ctx.db.insert("players", {
			player_id, display_name
		})
		return player_id;
	}
})

export const validateUserId = query({
	args: {
		user_id: v.string()
	},
	handler: async (ctx, args) => {
		const user = await ctx.db.query("players").filter((q) => q.eq(q.field("player_id"), args.user_id)).take(1);
		if (user.length === 0) {
			return "n"
		} else {
			return "y"
		}
	}
})

export const addUserToGame = mutation({
	args: {
		game_id: v.string(),
		user_id: v.string(),
		creator: v.boolean(),
	},
	handler: async (ctx, args) => {
		console.log(args)
		const games = await ctx.db.query('games').filter((q) => q.eq(q.field('game_id'), args.game_id)).take(1)
		if (games.length === 0 || games.length > 1) {
			return false;
		}
		const game = games[0]
		const current_players = game.player_ids ?? [];
		if (current_players.includes(args.user_id)) {
			return true;
		}
		const new_players = [...current_players, args.user_id];
		if (args.creator) {
			await ctx.db.patch(game._id, { player_ids: new_players, creator_id: args.user_id })
		} else {
			await ctx.db.patch(game._id, { player_ids: new_players })
		}
		return true;
	}
})

export const getGameData = query({
	args: {
		game_id: v.string(),
	},
	handler: async (ctx, args) => {
		const data = await ctx.db.query('games').filter((q) => q.eq(q.field('game_id'), args.game_id)).take(1);
		return data;
	}
})

export const userIdToName = query({
	args: {
		user_id: v.string(),
	},
	handler: async (ctx, args) => {
		const data = await ctx.db.query('players').filter((q) => q.eq(q.field('player_id'), args.user_id)).take(1);
		return data;
	}
})