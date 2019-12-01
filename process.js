res = [];
s = "";
for (r of res) {
	s +=`\n${r.name}: ${r.email} (${r.first_name} ${r.last_name}, ${r.username}): ${r.score}`;
}
console.log(s);