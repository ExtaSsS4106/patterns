class fetcher{
    constructor(){
        this.url = "https://script.google.com/macros/s/AKfycbxtM6plQ32ks16IUEZCZNLaVIn5CedilGWd4RjMGA27wVCRF2kj1MB7m4exrUSqjvr_/exec";
    }


    async getAllPatterns(){
        try{
            const response = await fetch(`${this.url}?action=getAllPatterns`);
            const data = await response.json();
            console.log(JSON.stringify(data));
            return data;
        }catch{
            return {"data": "error"}
        }
    }

    
    async getPatternById(id){
        if (!id){
            return "no id"
        }
        try{
            const response = await fetch(`${this.url}?action=getPatternById&id=${id}`);
            const data = await response.json();
            console.log(JSON.stringify(data));
            return data;
        }catch{
            return {"data": "error"}
        }
    }   

    async getCategories(){
        try{
            const response = await fetch(`${this.url}?action=getCategories`);
            const data = await response.json();
            console.log(JSON.stringify(data));
            return data;
        }catch{
            return {"data": "error"}
        }
    }  

    async getPatternsByCategories(id){
        if (!id){
            return "no id"
        }
        try{
            const response = await fetch(`${this.url}?action=getPatternsByCategories&category_id=${id}`);
            const data = await response.json();
            console.log(JSON.stringify(data));
            return data;
        }catch{
            return {"data": "error"}
        }
    }
}